# Generated by Django 4.2 on 2024-05-29 07:20

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('players_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Portfolio',
            new_name='Profile',
        ),
    ]
