from django.urls import path
from players_app.views import *

app_name = 'players_app'

urlpatterns = [
    # User views
    path('register/', PlayerRegisterView.as_view(), name='user_register'),
    path('login/', PlayerLoginView.as_view(), name='user_login'),
    path('logout/', PlayerLogoutView.as_view(), name='user_logout'),

    # PlayerRequest views
    path('request-create/', PlayerRequestCreateView.as_view(), name='request_create'),
    path('request-list/', PlayerRequestListView.as_view(), name='request_list'),
    path('request-switch/<int:pk>/', PlayerRequestSwitchView.as_view(), name='request_switch'),


    # Profile views
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile-change-privacy/', ProfileChangePrivacyView.as_view(), name='profile_change_privacy'),
    path('profile-list/', ProfileListView.as_view(), name='profile_list'),

    # GameCard views
    path('gamecard-create/', GameCardCreateView.as_view(), name='gamecard_create'),
    path('gamecard-detail/<int:pk>/', GameCardDetailView.as_view(), name='gamecard_detail'),
    path('gamecard-update/<int:pk>/', GameCardUpdateView.as_view(), name='gamecard_update'),
    path('gamecard-delete/<int:pk>/', GameCardDeleteView.as_view(), name='gamecard_delete'),
    path('gamecard-list-by-game/<int:game_pk>/', GameCardListByGameView.as_view(), name='gamecard_list_by_game'),

]
