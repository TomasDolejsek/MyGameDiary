# Generated by Django 4.2 on 2025-01-23 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games_app', '0009_alter_game_options_remove_game_serial_number_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['ordering_name', 'year']},
        ),
        migrations.AddField(
            model_name='game',
            name='ordering_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
