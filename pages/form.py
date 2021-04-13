from django import forms
from django.core import validators


AlphaDigitalTextValidator = validators.RegexValidator(r'^[a-zA-Z0-9]+$', 'Only alphanumeric characters are allowed.')
NicknameTextValidator = validators.RegexValidator(r'^[a-zA-Z0-9]{5,15}$', 'Only alphanumeric characters are allowed.')
SectionThemeNameValidator = validators.RegexValidator(r'^[а-яА-Яa-zA-Z0-9?! ]{1,75}$', 'Bad name.')


class LoginForm(forms.Form):
    nickname = forms.CharField(validators=[NicknameTextValidator])
    password = forms.CharField(validators=[AlphaDigitalTextValidator])


class SectionThemeForm(forms.Form):
    name = forms.CharField(validators=[SectionThemeNameValidator])


class UserRegistrationForm(forms.Form):
    email = forms.EmailField()
    nickname = forms.CharField(validators=[NicknameTextValidator])
    password = forms.CharField(validators=[AlphaDigitalTextValidator])
