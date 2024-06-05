from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from django.db.models import Sum

from games_app.models import Game


class Profile(models.Model):
    """
    Profile Model
    is linked one-to-one with the generic User django model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    register_date = models.DateField(default=datetime.today)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"

    @property
    def first_letter(self):
        return self.user.username[0]

    @property
    def is_admin(self):
        return self.user.groups.filter(name='Admin').exists()

    @property
    def total_gamecards(self):
        return GameCard.objects.on_profile(profile=self).count()

    @property
    def total_finished_games(self):
        return GameCard.objects.on_profile(profile=self).filter(is_finished=True).count()

    @property
    def total_hours(self):
        hours = GameCard.objects.on_profile(profile=self).aggregate(Sum('hours_played'))['hours_played__sum']
        if hours is None:
            hours = 0
        return hours

    @property
    def associated_games(self):
        gamecards = GameCard.objects.on_profile(profile=self)
        game_info = {
            'games': [x.game for x in gamecards],
            'gamecards_pk': gamecards.values_list('pk', flat=True)
        }
        print(game_info)
        return game_info

"""
GameCard Model
using GameCardManager for querying game cards
"""


class GameCardQuerySet(models.QuerySet):
    def on_profile(self, profile):
        if profile is not None:
            return self.filter(profile=profile)
        return GameCard.objects.none()  # return empty queryset

    def about_game(self, game):
        if game is not None:
            return self.filter(game=game)
        return GameCard.objects.none()  # return empty queryset

    def on_public_profiles(self, game):
        if game is not None:
            return self.about_game(game=game).filter(profile__is_private=False)
        return GameCard.objects.none()


class GameCardManager(models.Manager):
    def get_queryset(self):
        return GameCardQuerySet(self.model, using=self._db)

    def on_profile(self, profile):
        return self.get_queryset().on_profile(profile)

    def about_game(self, game):
        return self.get_queryset().about_game(game)

    def on_public_profiles(self, game):
        return self.get_queryset().on_public_profiles(game)


class GameCard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)
    hours_played = models.PositiveIntegerField(default=0)
    avatar_names = models.CharField(max_length=100, null=True, blank=True)
    review_link_url = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    objects = GameCardManager()

    class Meta:
        unique_together = (('profile', 'game'),)

    def __str__(self):
        return f"{self.profile.user.username} - {self.game.name}"

    @property
    def associated_game_name(self):
        return self.game.name

    @property
    def is_finished_text(self):
        return 'YES' if self.is_finished else 'NO'

    @property
    def avatar_names_text(self):
        return self.avatar_names if self.avatar_names else '---'

    def review_link_text(self):
        return self.review_link_url if self.review_link_url else '---'

