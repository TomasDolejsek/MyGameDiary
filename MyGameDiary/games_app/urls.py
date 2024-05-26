from django.urls import path
from games_app.views import *

app_name = 'games_app'

urlpatterns = [
    # Game views
    path('game-list/', GameListView.as_view(), name='game_list'),
    path('game-add/', GameAddView.as_view(), name='game_add'),
    path('game-add/<game_title>', GameSaveView.as_view(), name='game_save'),

    ]
