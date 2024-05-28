from django.urls import reverse_lazy
from django.views.generic import TemplateView
from players_app.views import UserRightsMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(TemplateView):
    template_name = 'index.html'


class SessionView(LoginRequiredMixin, UserRightsMixin, TemplateView):
    template_name = 'session.html'
    login_url = reverse_lazy('user_login')
    allowed_groups = ['Admin']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_rights())
        return context
