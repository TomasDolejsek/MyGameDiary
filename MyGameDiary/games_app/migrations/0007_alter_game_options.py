# Generated by Django 4.2 on 2024-06-21 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games_app', '0006_rename_clean_name_game_clear_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['clear_name']},
        ),
    ]