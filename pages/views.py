# pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import User


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_user = False
        if is_user:
            pass
        else:
            context['head'] = 'welcome.html'
        return context


