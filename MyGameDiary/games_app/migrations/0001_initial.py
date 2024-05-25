# Generated by Django 4.2 on 2024-05-24 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('year', models.IntegerField()),
                ('cover_url', models.URLField()),
                ('genres', models.ManyToManyField(to='games_app.genre')),
            ],
        ),
    ]
