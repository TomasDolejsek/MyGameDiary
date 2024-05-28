from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from players_app.models import Portfolio


class PlayerRegistrationForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            player_group = Group.objects.get(name='Player')
            user.groups.add(player_group)
            user.save()
            portfolio = Portfolio.objects.create(user=user)
            portfolio.save()
            return user
