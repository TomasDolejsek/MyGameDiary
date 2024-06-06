from django.forms import ModelForm, CheckboxInput, Textarea, TextInput, NumberInput
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
        fields = ['is_finished', 'hours_played', 'avatar_names', 'review_link', 'notes']

        widgets = {
                'is_finished': CheckboxInput(attrs={
                    'style': 'width:30px; height:30px;',
                    'class': "form-check-input",
                }),
                'hours_played': NumberInput(attrs={
                    'style': 'width:80px;',
                    'class': 'form-control',
                }),
                'notes': Textarea(attrs={
                    'style': 'width: 100%; height: 100px;',
                    'placeholder': 'Enter notes',
                    'class': 'form-control',
                }),
                'avatar_names': TextInput(attrs={
                    'placeholder': "Your in-game Character's Names",
                    'class': 'form-control',
                }),
                'review_link': TextInput(attrs={
                    'placeholder': 'A Link to Your Review, e.g. on Steam',
                    'class': "form-control",
                })
        }
