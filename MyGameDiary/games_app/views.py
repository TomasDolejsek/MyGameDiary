from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, FormView, RedirectView

from games_app.models import *
from games_app.forms import *
from games_app.api_utils import *


class GameListView(ListView):
    model = Game
    template_name = 'game-list.html'
    context_object_name = 'games'


class GameAddView(TemplateView):
    model = Game
    template_name = 'game-add.html'
    context_object_name = 'game'

    def get(self, *args, **kwargs):
        form = GameSearchApiForm()
        context = {'form': form}
        return render(self.request,
                      template_name=self.template_name,
                      context=context)

    def post(self, *args, **kwargs):
        form = GameSearchApiForm(self.request.POST)
        if form.is_valid():
            game_title = form.cleaned_data['name']
            return redirect('games_app:game_save', game_title)
        else:
            return HttpResponse('Bad data')


class GameSaveView(TemplateView):
    template_name = 'game-add.html'
    context_object_name = 'games'

    def get(self, *args, **kwargs):
        game_title = kwargs['game_title']
        games = find_game_id(game_title)
        context = {'game_title': game_title,
                   'games': games}
        return render(self.request,
                      template_name=self.template_name,
                      context=context)

    def post(self, *args, **kwargs):
        game_to_save = self.request.POST['game_to_save']
        game_id = game_to_save.split(',')[0]
        if save_game(game_id):
            save_to_file(game_to_save)
        return redirect('games_app:game_list')
