from django import forms


class GameSearchApiForm(forms.Form):
    name = forms.CharField(max_length=64,
                           label="Game Title",
                           help_text="Enter the game's title",
                           widget=forms.TextInput(),
                           required=True)
