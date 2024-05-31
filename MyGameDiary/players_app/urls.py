from django.urls import path
from players_app.views import *

app_name = 'players_app'

urlpatterns = [
    # User views
    path('register/', PlayerRegisterView.as_view(), name='user_register'),
    path('login/', PlayerLoginView.as_view(), name='user_login'),
    path('logout/', PlayerLogoutView.as_view(), name='user_logout'),

    # Profile views
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile-change-privacy/', ProfileChangePrivacyView.as_view(), name='profile_change_privacy'),
    path('profile-list/', ProfileListView.as_view(), name='profile_list'),

    # Gamecard views
    path('gamecard-create/', GameCardCreateView.as_view(), name='gamecard_create'),
    path('gamecard-detail/<int:pk>/', GameCardDetailView.as_view(), name='gamecard_detail'),\
    path('gamecard-update/<int:pk>/', GameCardUpdateView.as_view(), name='gamecard_update'),\

]
