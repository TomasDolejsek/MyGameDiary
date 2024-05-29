from django.urls import path
from players_app.views import *

app_name = 'players_app'

urlpatterns = [
    # user authentication
    path('register/', PlayerRegisterView.as_view(), name='user_register'),
    path('login/', PlayerLoginView.as_view(), name='user_login'),
    path('logout/', PlayerLogoutView.as_view(), name='user_logout'),

    # portfolio
    path('portfolio/<profile_pk>/', PortfolioView.as_view(), name='portfolio'),
    path('portfolio-change-privacy/', PortfolioChangePrivacyView.as_view(), name='portfolio_change_privacy'),

    # gamecards
    path('gamecard-create/', GameCardCreateView.as_view(), name='gamecard_create'),
    path('gamecard-detail/<pk>/', GameCardDetailView.as_view(), name='gamecard_detail'),


]
