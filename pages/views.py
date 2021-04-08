# pages/views.py
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.http import JsonResponse
from hashlib import sha256
import time
from .models import User, Session
from .form import LoginForm


SESSION_TIME_LENGTH = 60*60*24


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_user = False
        context['is_admin'] = False

        session_hash = self.request.COOKIES.get('session_hash')
        if session_hash is not None:
            try:
                session = Session.objects.get(hash=session_hash)
                now = int(time.time())
                if session.time+SESSION_TIME_LENGTH >= now:
                    user = User.objects.get(id=session.user.id)
                    if user.is_admin == 1:
                        context['is_admin'] = True
                    context['user_name'] = user.nickname
                    is_user = True
            except BaseException as error:
                print(error)

        if is_user:
            context['head'] = 'user_panel.html'
        else:
            context['head'] = 'welcome.html'
        return context


class LoginPageView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        data = {'ok': False}
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            try:
                user = User.objects.get(nickname=login_form.data['nickname'],
                                        password_hash=sha256(login_form.data['password'].encode('utf-8')).hexdigest())
                data['ok'] = True
                now = int(time.time())
                session_hash = sha256((str(now)+user.nickname+request.META['HTTP_USER_AGENT']).encode('utf-8')).hexdigest()
                Session.objects.create(user=user, hash=session_hash, time=now)
                data['session_hash'] = session_hash
            except BaseException as error:
                print(error)
        else:
            print('ooops')
        return JsonResponse(data)
