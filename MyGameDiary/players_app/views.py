from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, ListView, DetailView, UpdateView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from players_app.mixins import AnonymousRequiredMixin, ProfileOwnershipRequiredMixin, ProfileNotPrivateRequiredMixin
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

    def get(self, *args, **kwargs):
        self.profile_pk = self.request.GET.get('profile_pk')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context

    def get_queryset(self):
        try:
            self.profile = Profile.objects.filter(pk=self.profile_pk).first()
            if self.profile:
                return GameCard.objects.is_on_profile(profile=self.profile)
            else:
                messages.error(self.request, f"Profile with id {self.profile_pk} was not found in our database.")
        except ValueError:
            messages.error(self.request, f"'{self.profile_pk}' is not a valid profile id.")
        return GameCard.objects.none()


class ProfileChangePrivacyView(LoginRequiredMixin, ProfileOwnershipRequiredMixin, RedirectView):
    login_url = reverse_lazy('players_app:user_login')

    def change_privacy(self, profile_pk):
        try:
            profile_to_change_privacy = Profile.objects.filter(pk=profile_pk).first()
            if profile_to_change_privacy:
                profile_to_change_privacy.is_private = not profile_to_change_privacy.is_private
                profile_to_change_privacy.save()
                return True
            else:
                messages.error(self.request, f"Profile with id {profile_pk} was not found in our database.")
        except ValueError:
            messages.error(self.request, f"'{profile_pk}' is not a valid profile id.")
        return False

    def get(self, *args, **kwargs):
        profile_pk = self.request.GET.get('profile_pk')
        self.change_privacy(profile_pk)
        return redirect(reverse_lazy('players_app:profile') + '?profile_pk=' + profile_pk)


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profile-list.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'profiles'


class GameCardCreateView(LoginRequiredMixin, ProfileOwnershipRequiredMixin, RedirectView):
    login_url = reverse_lazy('players_app:user_login')
    url = reverse_lazy('games_app:game_list')

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
                messages.error(self.request, f"Game with id {associated_game_pk} was not found in our game database.")
        except ValueError:
            messages.error(self.request, f"'{associated_game_pk}' is not a valid game id.")
        except IntegrityError:
            messages.error(self.request, f"This game is already in your portfolio.")
        return super().get(self.request, *args, **kwargs)


class GameCardDetailView(LoginRequiredMixin, ProfileNotPrivateRequiredMixin, DetailView):
    model = GameCard
    template_name = 'gamecard-detail.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecard'


class GameCardUpdateView(LoginRequiredMixin, ProfileOwnershipRequiredMixin, UpdateView):
    model = GameCard
    template_name = 'gamecard-update.html'
    login_url = reverse_lazy('players_app:user_login')
    context_object_name = 'gamecard'
    success_url = reverse_lazy('players_app:profile')
    form_class = GameCardForm



