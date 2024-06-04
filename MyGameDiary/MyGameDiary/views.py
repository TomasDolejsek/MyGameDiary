from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from games_app.models import Game
from players_app.mixins import UserRightsMixin
from players_app.models import GameCard


class HomePageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_games'] = Game.objects.count()
        context['total_players'] = User.objects.count()
        context['total_gamecards'] = GameCard.objects.count()
        return context


class SessionView(LoginRequiredMixin, UserRightsMixin, TemplateView):
    template_name = 'session.html'
    login_url = reverse_lazy('players_app:user_login')
    allowed_groups = ['All']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_rights())
        return context
