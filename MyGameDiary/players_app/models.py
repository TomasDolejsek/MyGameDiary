from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
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
    def is_admin(self):
        return self.user.groups.filter(name='Admin').exists()


"""
GameCard Model
using GameCardManager for querying game cards
"""


class GameCardQuerySet(models.QuerySet):
    def is_on_profile(self, profile):
        if profile is not None:
            return self.filter(profile=profile)
        return GameCard.objects.none()  # return empty queryset


class GameCardManager(models.Manager):
    def get_queryset(self):
        return GameCardQuerySet(self.model, using=self._db)

    def is_on_profile(self, profile):
        return self.get_queryset().is_on_profile(profile)


class GameCard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)
    hours_played = models.PositiveIntegerField(null=True, blank=True)
    avatar_names = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    objects = GameCardManager()

    class Meta:
        unique_together = (('game', 'profile'),)

    def __str__(self):
        return f"{self.profile.user.username} - {self.game.name}"
