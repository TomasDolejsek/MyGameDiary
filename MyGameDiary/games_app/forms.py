from django import forms

from games_app.models import Game


class GameSearchApiForm(forms.Form):
    name = forms.CharField(max_length=64,
                           label="Search Game:",
                           help_text="Enter the game's title",
                           widget=forms.TextInput(),
                           required=True)
