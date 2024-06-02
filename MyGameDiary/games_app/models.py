from django.db import models


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


class Game(models.Model):
    name = models.CharField(max_length=100)
    cover_url = models.URLField()
    year = models.IntegerField()
    rating = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    perspectives = models.ManyToManyField(Perspective)

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return f"{self.name} ({self.year})"

    def get_genres_names(self):
        genres_names = []
        for genre in self.genres.all():
            genres_names.append(genre.name)
        return ', '.join(genres_names)

    def get_perspectives_names(self):
        perspectives_names = []
        for perspective in self.perspectives.all():
            perspectives_names.append(perspective.name)
        return ', '.join(perspectives_names)
