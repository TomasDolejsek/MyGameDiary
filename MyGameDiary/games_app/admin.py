from django.contrib import admin
from games_app.models import Genre, Perspective, Franchise, Game


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Perspective)
class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_games']

    @admin.display(description='Games')
    def get_games(self, obj):
        return list(Game.objects.of_franchise(franchise=obj).order_by('year'))


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'franchise', 'year', 'rating', 'cover_url', 'summary', 'get_genres', 'get_perspectives')

    @admin.display(description='Genres')
    def get_genres(self, obj):
        return obj.get_genres_names()

    @admin.display(description='Perspectives')
    def get_perspectives(self, obj):
        return obj.get_perspectives_names()
