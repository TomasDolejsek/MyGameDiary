from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from games_app.models import Game


class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    register_date = models.DateField(default=datetime.today)
