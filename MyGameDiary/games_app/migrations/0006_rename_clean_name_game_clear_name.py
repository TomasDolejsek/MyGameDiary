# Generated by Django 4.2 on 2024-06-09 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games_app', '0005_game_clean_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='clean_name',
            new_name='clear_name',
        ),
    ]