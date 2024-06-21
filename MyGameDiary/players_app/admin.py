from django.contrib import admin
from django.contrib.auth.models import Group
from players_app.models import Profile, GameCard, PlayerRequest, Version


@admin.register(GameCard)
class GameCardAdmin(admin.ModelAdmin):
    list_display = ['get_profile_username', 'get_game_name', 'finished', 'hours_played',
                    'avatar_names', 'review_link', 'notes']

    @admin.display(description='Player')
    def get_profile_username(self, obj):
        return obj.profile.user.username

    @admin.display(description='Game')
    def get_game_name(self, obj):
        return obj.game.name

    @admin.display(description='Finished')
    def finished(self, obj):
        return obj.is_finished_text


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'get_groups', 'register_date', 'is_private']

    @admin.display(description='Player')
    def get_username(self, obj):
        return obj.user.username

    @admin.display(description='Groups')
    def get_groups(self, obj):
        return list(obj.user.groups.all().values_list('name', flat=True))


@admin.register(PlayerRequest)
class PlayerRequestAdmin(admin.ModelAdmin):
    list_display = ['get_status', 'timestamp', 'get_player_name', 'text']

    @admin.display(description='Status')
    def get_status(self, obj):
        if obj.active:
            return 'Active'
        return 'Solved'

    @admin.display(description='Player')
    def get_player_name(self, obj):
        return obj.profile.user.username


@admin.register(Version)
class PlayerRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'description']



admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members')

    @admin.display(description='Members')
    def get_members(self, obj):
        if obj.name == 'Admin':
            members = list(obj.user_set.all().values_list('username', flat=True).order_by('username'))
        else:
            members = '--All--'
        return members


