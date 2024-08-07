"""
URL configuration for MyGameDiary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from MyGameDiary.views import HomePageView, HistoryPageView


urlpatterns = [
    # general views
    path('', HomePageView.as_view(), name='homepage'),
    path('admin/', admin.site.urls, name='admin'),
    path('history/', HistoryPageView.as_view(), name='history'),

    # apps views
    path('games/', include('games_app.urls', namespace='games_app')),
    path('players/', include('players_app.urls', namespace='players_app')),
]
