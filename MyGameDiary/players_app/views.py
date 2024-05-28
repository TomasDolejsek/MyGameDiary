from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from players_app.forms import PlayerRegistrationForm


def print_info(request):
    print(request.user)


class UserRightsMixin:
    allowed_groups = []

    @staticmethod
    def is_member_of(user, group_names):
        return user.groups.filter(name__in=group_names).exists()

    def get_context_rights(self):
        context = {'user_has_rights': self.is_member_of(self.request.user, self.allowed_groups)}
        return context


class PlayerLoginView(FormView):
    template_name = 'authenticate/user-login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Nice to see you, {self.request.user}!')
            return redirect(reverse_lazy('homepage'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return redirect(reverse_lazy('players_app:user_login'))


class PlayerLogoutView(LoginRequiredMixin, RedirectView):
    logged_user = None
    login_url = reverse_lazy('players_app:user_login')

    def get(self, *args, **kwargs):
        self.logged_user = self.request.user.username
        logout(self.request)
        return super().get(self.request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        messages.success(self.request, f'See you later, {self.logged_user}!')
        return reverse_lazy('homepage')


class PlayerRegisterView(FormView):
    template_name = 'authenticate/user-register.html'
    form_class = PlayerRegistrationForm
    success_url = reverse_lazy('players_app:user_login')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome, {self.request.user}! Please login.')
            return redirect(reverse_lazy('homepage'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please try again.')
        return redirect(reverse_lazy('players_app:user_register'))
