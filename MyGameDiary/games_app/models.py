from django.db import models
from django.db.models import Sum


class Genre(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Perspective(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return self.name


class GameQuerySet(models.QuerySet):
    def starts_with(self, query):
        return self.filter(clear_name__istartswith=query)


class GameManager(models.Manager):
    def get_queryset(self):
        return GameQuerySet(self.model, using=self._db)

    def starts_with(self, letter):
        return self.get_queryset().starts_with(letter)


class Game(models.Model):
    name = models.CharField(max_length=100)
    clear_name = models.CharField(max_length=100, null=True, blank=True)
    cover_url = models.URLField()
    year = models.IntegerField()
    rating = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    perspectives = models.ManyToManyField(Perspective)

    objects = GameManager()

    class Meta:
        ordering = ['clear_name', ]

    def __str__(self):
        return f"{self.name} ({self.year})"

    def get_genres_names(self):
        genres_names = []
        genres = self.genres.all()
        if not genres:
            return '---'
        for genre in genres:
            genres_names.append(genre.name)
        return ', '.join(genres_names)

    def get_perspectives_names(self):
        perspectives_names = []
        perspectives = self.perspectives.all()
        if not perspectives:
            return '---'
        for perspective in perspectives:
            perspectives_names.append(perspective.name)
        return ', '.join(perspectives_names)

    @property
    def rating_text(self):
        if self.rating is None:
            return '---'
        return f"{self.rating} / 100"

    @property
    def total_gamecards(self):
        from players_app.models import GameCard
        return GameCard.objects.about_game(game=self).count()

    @property
    def public_gamecards(self):
        from players_app.models import GameCard
        return GameCard.objects.on_public_profiles(game=self).count()

    @property
    def private_gamecards(self):
        return self.total_gamecards - self.public_gamecards

    def total_finished(self):
        from players_app.models import GameCard
        return GameCard.objects.about_game(game=self).filter(is_finished=True).count()

    def total_hours(self):
        from players_app.models import GameCard
        hours = GameCard.objects.about_game(game=self).aggregate(Sum('hours_played'))['hours_played__sum']
        if hours is None:
            hours = 0
        return hours
