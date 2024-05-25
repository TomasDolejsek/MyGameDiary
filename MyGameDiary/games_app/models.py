from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.pk} - {self.name}"


class Game(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    cover_url = models.URLField()
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return f"{self.pk} - {self.name} - {self.year}"
