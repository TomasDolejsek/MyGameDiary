from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView

from games_app.models import Game
from players_app.models import GameCard, Version


class HomePageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_games'] = Game.objects.count()
        context['total_players'] = User.objects.count()
        context['total_gamecards'] = GameCard.objects.count()
        return context


class HistoryPageView(ListView):
    model = Version
    template_name = 'history.html'
    context_object_name = 'versions'
