from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from players_app.mixins import (AnonymousRequiredMixin, ProfileOwnershipRequiredMixin, ProfileNotPrivateRequiredMixin,
                                GameCardOwnershipRequiredMixin, GameCardNotPrivateRequiredMixin, UserRightsMixin,
                                LimitPendingRequestsMixin)

from players_app.forms import PlayerRegistrationForm, PlayerAuthenticationForm, GameCardForm, RequestForm
from players_app.models import GameCard, Profile, PlayerRequest
from games_app.models import Game

from django.db.models import Sum
from string import ascii_lowercase


class PlayerLoginView(AnonymousRequiredMixin, FormView):
    template_name = 'authentication/user-login.html'
    form_class = PlayerAuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            user_title = "MIGHTY ADMIN " if user.profile.is_admin else ''
            messages.success(self.request, f'Nice to see you, {user_title + self.request.user.username}!')
            return redirect(reverse_lazy('homepage'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return redirect(reverse_lazy('players_app:user_login'))


class PlayerLogoutView(LoginRequiredMixin, RedirectView):
    logged_user = None
    login_url = reverse_lazy('players_app:user_login')

    def get(self, *args, **kwargs):
        user_title = "MIGHTY ADMIN " if self.request.user.profile.is_admin else ''
        self.logged_user = user_title + self.request.user.username
        logout(self.request)
        return super().get(self.request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        messages.success(self.request, f'See you later, {self.logged_user}!')
        return reverse_lazy('homepage')


class PlayerRegisterView(AnonymousRequiredMixin, FormView):
    template_name = 'authentication/user-register.html'
    form_class = PlayerRegistrationForm
    success_url = reverse_lazy('players_app:user_login')
    registered_user = None

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        self.registered_user = username
        user = authenticate(username=username, password=password)
        if user is not None:
            messages.success(self.request, f"Registration successful. Welcome, {self.registered_user}! Please login.")
            return redirect(reverse_lazy('players_app:user_login'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please try again.")
        return redirect(reverse_lazy('players_app:user_register'))


class PlayerRequestCreateView(LoginRequiredMixin, LimitPendingRequestsMixin, CreateView):
    model = PlayerRequest
    template_name = 'request-create.html'
    form_class = RequestForm
    login_url = reverse_lazy('players_app:user_login')
    max_requests = 5

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.profile = self.request.user.profile
        instance.save()
        messages.success(self.request, "Request successfully created. Thank you!")
        return redirect(reverse_lazy('homepage'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_count = PlayerRequest.objects.by_profile(profile=self.request.user.profile).pending().count()
        context['requests_remaining'] = self.max_requests - query_count
        return context


class PlayerRequestListView(LoginRequiredMixin, UserRightsMixin, ListView):
    model = PlayerRequest
    template_name = 'request-list.html'
    context_object_name = 'player_requests'
    login_url = reverse_lazy('players_app:user_login')
    allowed_groups = ['Admin']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_rights())
        context['display'] = self.request.GET.get('display')
        return context

    def get_queryset(self):
        display = self.request.GET.get('display')
        if display == 'active':
            return PlayerRequest.objects.pending().order_by('-timestamp')
        elif display == 'solved':
            return PlayerRequest.objects.solved().order_by('-timestamp')
        else:
            return PlayerRequest.objects.all().order_by('-timestamp')


class PlayerRequestSwitchView(LoginRequiredMixin, UserRightsMixin, RedirectView):
    login_url = reverse_lazy('players_app:user_login')
    allowed_groups = ['Admin']

    def change_status(self, request_pk):
        try:
            request_to_change_status = PlayerRequest.objects.filter(pk=request_pk).first()
            if request_to_change_status:
                request_to_change_status.active = not request_to_change_status.active
                request_to_change_status.save()
                return True
            else:
                messages.error(self.request, f"Player Request was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid Player Request ID.")
        return False

    def get_redirect_url(self, *args, **kwargs):
        display = self.request.GET.get('display')
        return reverse_lazy('players_app:request_list') + f'?display={display}'

    def get(self, *args, **kwargs):
        request_pk = self.kwargs.get('pk')
        self.change_status(request_pk)
        return super().get(*args, **kwargs)


class ProfileView(LoginRequiredMixin, ProfileNotPrivateRequiredMixin, ListView):
    model = GameCard
    template_name = 'profile.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecards'
    profile_pk = None
    profile = None

    def dispatch(self, *args, **kwargs):
        self.profile_pk = self.kwargs['pk']
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['total_gamecards'] = GameCard.objects.on_profile(self.profile).count()

        context['letters'] = ascii_lowercase
        context['display'] = self.request.GET.get('display')
        return context

    def get_queryset(self):
        display = self.request.GET.get('display')
        try:
            self.profile = Profile.objects.filter(pk=self.profile_pk).first()
            if self.profile:
                if display == 'all':
                    return GameCard.objects.on_profile(profile=self.profile)
                return GameCard.objects.on_profile(profile=self.profile).starts_with(letter=display)
            else:
                messages.error(self.request, f"Profile was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid profile ID.")
        return GameCard.objects.none()


class ProfileChangePrivacyView(LoginRequiredMixin, ProfileOwnershipRequiredMixin, RedirectView):
    login_url = reverse_lazy('players_app:user_login')
    profile_pk = None

    def dispatch(self, *args, **kwargs):
        self.profile_pk = self.request.GET.get('profile_pk')
        return super().dispatch(*args, **kwargs)

    def change_privacy(self, profile_pk):
        try:
            profile_to_change_privacy = Profile.objects.filter(pk=profile_pk).first()
            if profile_to_change_privacy:
                profile_to_change_privacy.is_private = not profile_to_change_privacy.is_private
                profile_to_change_privacy.save()
                return True
            else:
                messages.error(self.request, f"Profile was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid profile ID.")
        return False

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('players_app:profile', kwargs={'pk': self.profile_pk}) + '?display=all'

    def get(self, *args, **kwargs):
        self.change_privacy(self.profile_pk)
        return super().get(*args, **kwargs)


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profile-list.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'profiles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_profiles'] = Profile.objects.all().count()
        context['total_private'] = Profile.objects.filter(is_private=True).count()
        context['total_gamecards'] = GameCard.objects.count()
        context['total_finished'] = GameCard.objects.filter(is_finished=True).count()
        context['total_hours'] = GameCard.objects.aggregate(Sum('hours_played'))['hours_played__sum']
        return context

    def get_queryset(self):
        return Profile.objects.select_related('user')


class GameCardCreateView(LoginRequiredMixin, ProfileOwnershipRequiredMixin, RedirectView):
    login_url = reverse_lazy('players_app:user_login')
    profile_pk = None

    def dispatch(self, *args, **kwargs):
        self.profile_pk = self.request.GET.get('profile_pk')
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        associated_profile = self.request.user.profile
        associated_game_pk = self.request.GET.get('game_pk')
        try:
            associated_game = Game.objects.filter(pk=associated_game_pk).first()
            if associated_game:
                GameCard.objects.create(profile=associated_profile, game=associated_game)
                messages.success(self.request, f"{associated_game.name} was added to your "
                                               f"game profile.")
            else:
                messages.error(self.request, f"Game was not found in our game database.")
        except ValueError:
            messages.error(self.request, "Invalid game ID.")
        except IntegrityError:
            messages.error(self.request, f"This game is already in your portfolio.")
        return super().get(self.request, *args, **kwargs)

    @staticmethod
    def get_redirect_url(*args, **kwargs):
        return reverse_lazy('games_app:game_list') + '?display=all'


class GameCardDetailView(LoginRequiredMixin, GameCardNotPrivateRequiredMixin, DetailView):
    model = GameCard
    template_name = 'gamecard-detail.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecard'
    gamecard_pk = None

    def dispatch(self, *args, **kwargs):
        self.gamecard_pk = kwargs['pk']
        return super().dispatch(*args, **kwargs)


class GameCardUpdateView(LoginRequiredMixin, GameCardOwnershipRequiredMixin, UpdateView):
    model = GameCard
    template_name = 'gamecard-update.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecard'
    form_class = GameCardForm
    gamecard_pk = None

    def dispatch(self, *args, **kwargs):
        self.gamecard_pk = self.kwargs['pk']
        return super().dispatch(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        messages.success(self.request, "Game Card Successfully Updated.")
        return reverse_lazy('players_app:gamecard_detail', kwargs={'pk': self.gamecard_pk})


class GameCardDeleteView(LoginRequiredMixin, GameCardOwnershipRequiredMixin, DeleteView):
    model = GameCard
    template_name = 'gamecard-delete.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecard'
    gamecard_pk = None
    game_name = None

    def dispatch(self, *args, **kwargs):
        self.gamecard_pk = self.kwargs['pk']
        self.game_name = GameCard.objects.filter(pk=self.gamecard_pk).first().associated_game_name
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        messages.warning(self.request, f"{self.game_name} was removed from your profile.")
        return super().post(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('players_app:profile', kwargs={'pk': self.request.user.profile.pk}) + '?display=all'


class GameCardListByGameView(LoginRequiredMixin, ListView):
    model = GameCard
    template_name = 'gamecard-list-by-game.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecards'
    game = None

    def get_queryset(self):
        game_pk = self.kwargs['game_pk']
        try:
            self.game = Game.objects.filter(pk=game_pk).first()
            if self.game:
                return GameCard.objects.on_public_profiles(game=self.game).order_by('profile__user__username')
            else:
                messages.error(self.request, f"Game was not found in our database.")
        except ValueError:
            messages.error(self.request, "Invalid game ID.")
        return GameCard.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.game
        gamecard = GameCard.objects.about_game(game=self.game).on_profile(profile=self.request.user.profile).first()
        context['gamecard_pk'] = gamecard.pk if gamecard is not None else None
        return context
