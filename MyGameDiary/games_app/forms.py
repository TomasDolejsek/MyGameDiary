from django import forms


class GameSearchApiForm(forms.Form):
    name = forms.CharField(max_length=64,
                           min_length=3,
                           label="Search Game:",
                           help_text="Enter the game's title",
                           widget=forms.TextInput(attrs={
                                'placeholder': "Game Title",
                                'class': 'form-control',
                           }),
                           required=True)
