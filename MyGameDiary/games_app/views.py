from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from players_app.mixins import UserRightsMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView
from django.utils.datastructures import MultiValueDictKeyError

from games_app.forms import GameSearchApiForm
from games_app.api_utils import find_game_id, save_game, save_to_file
from games_app.models import Game
from players_app.models import GameCard
from django.db.models import Sum

from string import ascii_lowercase


class GameAddView(LoginRequiredMixin, UserRightsMixin, TemplateView):
    model = Game
    template_name = 'game-add.html'
    context_object_name = 'game'
    login_url = reverse_lazy('players_app:user_login')
    allowed_groups = ['Admin']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_rights())
        return context

    def get(self, *args, **kwargs):
        form = GameSearchApiForm()
        context = self.get_context_data()
        context.update({'form': form})
        return render(self.request,
                      template_name=self.template_name,
                      context=context)

    def post(self, *args, **kwargs):
        form = GameSearchApiForm(self.request.POST)
        if form.is_valid():
            game_title = form.cleaned_data['name']
            return redirect(reverse_lazy('games_app:game_save', kwargs={'game_title': game_title}))


class GameSaveView(LoginRequiredMixin, UserRightsMixin, TemplateView):
    template_name = 'game-add.html'
    context_object_name = 'games'
    login_url = reverse_lazy('players_app:user_login')
    allowed_groups = ['Admin']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_context_rights())
        return context

    def get(self, *args, **kwargs):
        game_title = kwargs['game_title']
        context = self.get_context_data()
        if context['user_has_rights']:
            games = find_game_id(game_title)
            context.update({
                'game_title': game_title,
                'games': games,
                'total_games': len(games)
            })
        return render(self.request,
                      template_name=self.template_name,
                      context=context)

    def post(self, *args, **kwargs):
        try:
            game_to_save = self.request.POST['game_to_save']
            game_id, game_title = game_to_save.split(',')
            if save_game(game_id):
                save_to_file(game_to_save)
                messages.success(self.request, f"{game_title} successfully saved.")
            else:
                messages.error(self.request, f"{game_title} is already in the database.")
            return redirect(reverse_lazy('games_app:game_list') + '?display=all')
        except MultiValueDictKeyError:
            messages.error(self.request, "No game was selected.")
            return redirect(reverse_lazy('games_app:game_list') + '?display=all')


class GameListView(ListView):
    model = Game
    template_name = 'game-list.html'
    context_object_name = 'games'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games = context['games']
        games_data = []
        for game in games:
            game_dict = {}
            game_dict['game'] = game
            if self.request.user.is_authenticated:
                query = GameCard.objects.about_game(game=game).on_profile(profile=self.request.user.profile).first()
                game_dict['gamecard_pk'] = query.pk if query is not None else None
            else:
                game_dict['gamecard_pk'] = None
            games_data.append(game_dict)

        context['total_games'] = Game.objects.count()
        context['total_gamecards'] = GameCard.objects.count()
        context['total_finished'] = GameCard.objects.filter(is_finished=True).count()
        context['total_hours'] = GameCard.objects.aggregate(Sum('hours_played'))['hours_played__sum']
        context['games_data'] = games_data

        context['letters'] = ascii_lowercase
        context['display'] = self.request.GET.get('display')
        return context

    def get_queryset(self):
        display = self.request.GET.get('display')
        if display == 'all':
            return Game.objects.all()
        return Game.objects.starts_with(letter=display)


class GameDetailView(DetailView):
    model = Game
    template_name = 'game-detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            gamecard = (GameCard.objects.about_game(game=context['game'])
                        .on_profile(profile=self.request.user.profile).first())
            gamecard_pk = gamecard.pk if gamecard is not None else None
        else:
            gamecard_pk = None
        context['gamecard_pk'] = gamecard_pk
        return context
