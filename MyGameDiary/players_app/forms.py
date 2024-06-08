from django.forms import ModelForm, CheckboxInput, Textarea, TextInput, NumberInput, CharField, PasswordInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group, User

from players_app.models import Profile, GameCard


class PlayerRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={
            'style': 'width: 50%;',
            'placeholder': 'Your Password',
            'class': 'form-control'
        })

        self.fields['password1'].help_text = (
            "Please follow these rules:"
            "<ul>"
            "<li>Your password can’t be too similar to your username.</li>"
            "<li>Your password must contain at least 8 characters.</li>"
            "<li>Your password can’t be a commonly used password.</li>"
            "<li>Your password can’t be entirely numeric.</li>"
            "</ul>"
        )

        self.fields['password2'].widget = PasswordInput(attrs={
            'style': 'width: 50%;',
            'placeholder': 'Retype Your Password',
            'class': 'form-control'
        })

    username = CharField(min_length=5,
                         max_length=20,
                         help_text='Enter your username, 5-20 characters long.',
                         widget=TextInput(attrs={
                             'style': 'width: 50%',
                             'placeholder': 'Your Username',
                             'class': 'form-control'}),
                         required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

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


class PlayerAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = PasswordInput(attrs={
            'style': 'width: 50%;',
            'placeholder': 'Your Password',
            'class': 'form-control'
        })

    username = CharField(min_length=5,
                         max_length=20,
                         help_text='Enter your username',
                         widget=TextInput(attrs={
                             'style': 'width: 50%',
                             'placeholder': 'Your Username',
                             'class': 'form-control'}),
                         required=True)


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
