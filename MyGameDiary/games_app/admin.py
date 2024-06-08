from django.contrib import admin
from games_app.models import Genre, Perspective, Game


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Perspective)
class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'cover_url', 'year', 'rating', 'summary', 'get_genres', 'get_perspectives')

    @admin.display(description='Genres')
    def get_genres(self, obj):
        return obj.get_genres_names()

    @admin.display(description='Perspectives')
    def get_perspectives(self, obj):
        return obj.get_perspectives_names()

