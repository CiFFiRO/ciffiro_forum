# pages/urls.py
from django.urls import path, re_path
from .views import HomePageView, LoginPageView, ExitView, AddSectionPageView, SectionPageView, AddThemePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('exit/', ExitView.as_view(), name='exit'),
    path('add_section/', AddSectionPageView.as_view(), name='add_section'),
    re_path(r'^section/\d+/$', SectionPageView.as_view(), name='section'),
    re_path(r'^section/\d+/add_theme/$', AddThemePageView.as_view(), name='add_theme')
]
