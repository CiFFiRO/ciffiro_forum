# pages/urls.py
from django.urls import path
from .views import HomePageView, LoginPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login')
]
