# Generated by Django 4.2 on 2024-06-09 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games_app', '0004_perspective_game_rating_game_summary_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='clean_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
