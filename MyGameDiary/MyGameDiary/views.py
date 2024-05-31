from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from players_app.mixins import UserRightsMixin


class HomePageView(TemplateView):
    template_name = 'homepage.html'


class SessionView(LoginRequiredMixin, UserRightsMixin, TemplateView):
    template_name = 'session.html'
    login_url = reverse_lazy('players_app:user_login')
    allowed_groups = ['All']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_rights())
        return context
