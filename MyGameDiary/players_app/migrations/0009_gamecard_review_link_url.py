# Generated by Django 4.2 on 2024-06-05 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players_app', '0008_alter_gamecard_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamecard',
            name='review_link_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
