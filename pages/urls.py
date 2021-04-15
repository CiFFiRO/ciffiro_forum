# pages/urls.py
from django.urls import path, re_path
from .views import HomePageView, LoginPageView, ExitView, AddSectionPageView, \
    SectionPageView, AddThemePageView, ThemePageView, RegistrationPageView, ProfilePageView, MailboxPageView
from django.views.generic import RedirectView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('exit/', ExitView.as_view(), name='exit'),
    path('add_section/', AddSectionPageView.as_view(), name='add_section'),
    re_path(r'^section/\d+/$', SectionPageView.as_view(), name='section'),
    re_path(r'^section/\d+/add_theme/$', AddThemePageView.as_view(), name='add_theme'),
    re_path(r'^theme/\d+/$', ThemePageView.as_view(), name='theme'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico'), name='favicon'),
    path('registration/', RegistrationPageView.as_view(), name='registration'),
    re_path(r'^profile/\d+/$', ProfilePageView.as_view(), name='profile'),
    re_path(r'^mailbox/((income)|(outgoing))/$', MailboxPageView.as_view(), name='mailbox'),
]
