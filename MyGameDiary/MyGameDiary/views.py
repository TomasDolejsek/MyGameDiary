from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, RedirectView

# user authentication imports
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin


# homepage
class HomePageView(TemplateView):
    template_name = 'index.html'


# player
class PlayerLoginView(FormView):
    template_name = 'player-login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect(reverse_lazy('homepage'))
        return super().form_valid(form)


class PlayerLogoutView(RedirectView):
    logged_user = None

    def get(self, *args, **kwargs):
        self.logged_user = self.request.user.username
        logout(self.request)
        return super().get(self.request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('homepage') + '?username=' + self.logged_user
