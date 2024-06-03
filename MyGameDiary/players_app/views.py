from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from players_app.mixins import (AnonymousRequiredMixin, ProfileOwnershipRequiredMixin, ProfileNotPrivateRequiredMixin,
                                GameCardOwnershipRequiredMixin, GameCardNotPrivateRequiredMixin)
from django.contrib.auth.forms import AuthenticationForm
from players_app.forms import PlayerRegistrationForm, GameCardForm
from players_app.models import GameCard, Profile
from games_app.models import Game


class PlayerLoginView(AnonymousRequiredMixin, FormView):
    template_name = 'authentication/user-login.html'
    form_class = AuthenticationForm

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
        return context

    def get_queryset(self):
        try:
            self.profile = Profile.objects.filter(pk=self.profile_pk).first()
            if self.profile:
                return GameCard.objects.on_profile(profile=self.profile)
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
        return reverse_lazy('players_app:profile', kwargs={'pk': self.profile_pk})

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
        return context

    def get_queryset(self):
        return Profile.objects.select_related('user').order_by('user__username')


class GameCardCreateView(LoginRequiredMixin, ProfileOwnershipRequiredMixin, RedirectView):
    login_url = reverse_lazy('players_app:user_login')
    url = reverse_lazy('games_app:game_list')
    profile_pk = None

    def dispatch(self, *args, **kwargs):
        self.profile_pk = self.request.GET.get('profile_pk')
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        associated_profile = self.request.user.profile
        associated_game_pk = self.request.GET.get('game_id')
        try:
            associated_game = Game.objects.filter(pk=associated_game_pk).first()
            if associated_game:
                GameCard.objects.create(profile=associated_profile, game=associated_game)
                messages.success(self.request, f"{associated_game.name} (id: {associated_game_pk}) was added to your "
                                               f"game portfolio.")
            else:
                messages.error(self.request, f"Game was not found in our game database.")
        except ValueError:
            messages.error(self.request, "Invalid game ID.")
        except IntegrityError:
            messages.error(self.request, f"This game is already in your portfolio.")
        return super().get(self.request, *args, **kwargs)


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
        return reverse_lazy('players_app:profile', kwargs={'pk': self.request.user.profile.pk})


class GameCardDeleteView(LoginRequiredMixin, GameCardOwnershipRequiredMixin, DeleteView):
    model = GameCard
    template_name = 'gamecard-delete.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecard'
    gamecard_pk = None

    def dispatch(self, *args, **kwargs):
        self.gamecard_pk = self.kwargs['pk']
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        messages.warning(self.request, f"Game Card was removed from your portfolio.")
        return super().post(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('players_app:profile', kwargs={'pk': self.request.user.profile.pk})
