# Generated by Django 4.2 on 2024-06-06 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players_app', '0009_gamecard_review_link_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gamecard',
            old_name='review_link_url',
            new_name='review_link',
        ),
    ]
