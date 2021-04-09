from django import forms
from django.core import validators


AlphaDigitalTextValidator = validators.RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed.')
SectionThemeNameValidator = validators.RegexValidator(r'^[а-яА-Яa-zA-Z0-9?! ]+$', 'Bad name.')


class LoginForm(forms.Form):
    nickname = forms.CharField(validators=[AlphaDigitalTextValidator])
    password = forms.CharField(validators=[AlphaDigitalTextValidator])


class SectionForm(forms.Form):
    name = forms.CharField(validators=[SectionThemeNameValidator])

