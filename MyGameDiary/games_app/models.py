from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    cover_url = models.URLField()
    genres = models.ManyToManyField(Genre)

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return f"id: {self.pk} - '{self.name}' ({self.year})"

    def get_genres_names(self):
        genres_names = []
        for genre in self.genres.all():
            genres_names.append(genre.name)
        return ', '.join(genres_names)
