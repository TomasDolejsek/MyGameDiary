from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from players_app.models import Profile, GameCard


class PlayerRegistrationForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            player_group = Group.objects.get(name='Player')
            user.groups.add(player_group)
            user.save()
            profile = Profile.objects.create(user=user)
            profile.save()
            return user


class GameCardForm(ModelForm):
    class Meta:
        model = GameCard
        fields = ['is_finished']
