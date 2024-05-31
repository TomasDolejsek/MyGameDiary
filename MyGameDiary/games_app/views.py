from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from players_app.mixins import UserRightsMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView

from games_app.forms import GameSearchApiForm
from games_app.api_utils import find_game_id, save_game, save_to_file
from games_app.models import Game


class GameListView(ListView):
    model = Game
    template_name = 'game-list.html'
    context_object_name = 'games'


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
            return redirect(reverse_lazy('games_app:game_save'), game_title)
        else:
            return HttpResponse('Bad data')


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
            context.update({'game_title': game_title, 'games': games})
        return render(self.request,
                      template_name=self.template_name,
                      context=context)

    def post(self, *args, **kwargs):
        game_to_save = self.request.POST['game_to_save']
        game_id = game_to_save.split(',')[0]
        if save_game(game_id):
            save_to_file(game_to_save)
            messages.success(self.request, 'Game successfully saved.')
        else:
            messages.error(self.request, 'Game is already in the database.')
        return redirect(reverse_lazy('games_app:game_list'))
