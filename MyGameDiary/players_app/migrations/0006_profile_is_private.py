# Generated by Django 4.2 on 2024-05-29 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players_app', '0005_alter_gamecard_avatar_names_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
