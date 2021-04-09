# pages/urls.py
from django.urls import path
from .views import HomePageView, LoginPageView, ExitView, AddSectionPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('exit/', ExitView.as_view(), name='exit'),
    path('add_section/', AddSectionPageView.as_view(), name='add_section')
]
