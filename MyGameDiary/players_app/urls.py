from django.urls import path
from players_app.views import *

app_name = 'players_app'

urlpatterns = [
    path('register/', PlayerRegisterView.as_view(), name='user_register'),
    path('login/', PlayerLoginView.as_view(), name='user_login'),
    path('logout/', PlayerLogoutView.as_view(), name='user_logout'),
]
