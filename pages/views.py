# pages/views.py
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from hashlib import sha256
import time
from .models import User, Session, Section, Theme, Post, RegistrationForm
from .form import LoginForm, SectionThemeForm, UserRegistrationForm
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings


SESSION_TIME_LENGTH = 60*60*24
REGISTRATION_CODE_TIME_LIFE = 60*60*24


def user_by_session(request):
    session_hash = request.COOKIES.get('session_hash')
    if session_hash is not None:
        try:
            session = Session.objects.get(hash=session_hash)
            now = int(time.time())
            if session.time + SESSION_TIME_LENGTH >= now:
                user = User.objects.get(id=session.user.id)
                return user
        except BaseException as error:
            pass
    return None


def page_by_request(request):
    page = None
    try:
        page = int(request.GET['page'])
        page = page if page > 0 else 1
    except BaseException:
        page = 1
    return page


def set_user_context(context, request):
    is_user = False
    context['is_admin'] = False
    user = user_by_session(request)

    if user is not None:
        if user.is_admin == 1:
            context['is_admin'] = True
        context['user_name'] = user.nickname
        context['user_now_id'] = user.id
        is_user = True

    context['is_user'] = is_user

    if is_user:
        context['head'] = 'user_panel.html'
    else:
        context['head'] = 'welcome.html'


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_context(context, self.request)

        context['sections'] = []
        sections = Section.objects.all()
        for section in sections:
            data = {'name': section.name}
            number_themes = Theme.objects.raw(f'select 1 as id, count(*) as cnt from `forum`.`theme` '
                                       f'where `theme`.`section_id` = {section.id}')
            number_posts = Post.objects.raw(f'select 1 as id, sum(tb.cnt) as res from '
                                     f'(select distinct `theme`.`id` as t_id, count(`post`.`id`) as cnt from `forum`.`post`, `forum`.`theme`'
                                     f'where `theme`.`section_id` = {section.id} and `theme`.`id` = `post`.`theme_id`) as tb')
            data['number_themes'] = number_themes[0].cnt
            data['number_posts'] = number_posts[0].res
            if number_posts[0].res == 0:
                data['date_last_post'] = 'Нет сообщений'
            else:
                last_post = Post.objects.raw(f'select 1 as id, max(`post`.`datetime`) as res from `forum`.`post`, `forum`.`theme`' 
                                            f'where `theme`.`section_id` = {section.id} and `theme`.`id` = `post`.`theme_id`')
                data['date_last_post'] = last_post[0].res
            data['id'] = section.id
            context['sections'].append(data)

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


class ExitView(LogoutView):
    def post(self, request, *args, **kwargs):
        session_hash = request.COOKIES.get('session_hash')
        if session_hash is not None:
            try:
                session = Session.objects.get(hash=session_hash)
                session.time = 0
                session.save(update_fields=["time"])
            except BaseException as error:
                pass
        return JsonResponse({})


class AddSectionPageView(FormView):
    template_name = 'add_section_theme.html'
    form_class = SectionThemeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_section'] = True
        context['is_theme'] = False
        context['path_request'] = "/add_section/"
        user = user_by_session(self.request)
        if user is None or not user.is_admin:
            raise PermissionDenied()
        return context

    def post(self, request, *args, **kwargs):
        data = {'ok': False}
        section_form = SectionThemeForm(request.POST)
        user = user_by_session(self.request)

        if user is None or not user.is_admin:
            raise PermissionDenied()

        if section_form.is_valid():
            try:
                Section.objects.create(name=section_form.data['name'])
                data['ok'] = True
            except BaseException as error:
                print(error)
        else:
            print('ooops')
        return JsonResponse(data)


class SectionPageView(TemplateView):
    template_name = 'section.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_context(context, self.request)
        section_id_index = -2
        section_id = int(self.request.path.split('/')[section_id_index])
        page = page_by_request(self.request)
        try:
            section = Section.objects.get(id=section_id)
            context['section_id'] = section.id
            context['section_name'] = section.name
        except BaseException:
            raise PermissionDenied()
        context['page'] = page
        themes_by_page = 5
        width_paginator = 1

        number_posts = Theme.objects.raw(
            f'select 1 as id, count(*) as cnt from `forum`.`theme` where `theme`.`section_id` = {section_id}')
        number_pages = 0
        if len(number_posts) == 1:
            number_pages = (number_posts[0].cnt // themes_by_page) + (
                1 if number_posts[0].cnt % themes_by_page > 0 else 0)
        context['number_pages'] = number_pages
        context['width_paginator'] = width_paginator
        context['window_pages'] = list(range(max(page - width_paginator, 2),
                                             min(page + width_paginator, number_pages - 1) + 1))
        context['page_path'] = f'/section/{section_id}/'

        themes = Theme.objects.raw(f'select id, name, time, cnt from '
                                   f'(select id, name, max(time) as time, count(post_id) as cnt  from  '
                                   f'(select tb1.`id`, tb1.`name`,  '
                                   f'case when tb2.`datetime` is null then tb1.`datetime` else tb2.`datetime` end as time,  '
                                   f'tb2.`id` as post_id '
                                   f'from `forum`.`theme` as tb1 left join `forum`.`post` as tb2 on tb1.id = tb2.theme_id  '
                                   f'where tb1.section_id = {section_id}) as tb group by id, name) as tb1 '
                                   f'order by time desc limit {(page-1)*themes_by_page}, {themes_by_page} ')
        context['themes'] = []
        for theme in themes:
            if theme.id is None:
                break
            data = {'id': theme.id, 'name': theme.name, 'number_posts': theme.cnt, 'date_last_post': theme.time}
            data['date_last_post'] = data['date_last_post'] if theme.cnt > 0 else 'Нет сообщений'
            context['themes'].append(data)

        return context

    def post(self, request, *args, **kwargs):
        section_id_index = -2
        section_id = int(self.request.path.split('/')[section_id_index])
        user = user_by_session(self.request)
        data = {'ok': False}

        if user is None:
            raise PermissionDenied()

        if request.POST['is_delete_section'] == 'true':
            if not user.is_admin:
                raise PermissionDenied()
            try:
                section = Section.objects.get(id=section_id)
                section.delete()
                data = {'ok': True}
            except BaseException:
                raise PermissionDenied()

        return JsonResponse(data)


class AddThemePageView(FormView):
    template_name = 'add_section_theme.html'
    form_class = SectionThemeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_section'] = False
        context['is_theme'] = True
        section_id_index = -3
        section_id = int(self.request.path.split('/')[section_id_index])
        context['section_id'] = section_id
        context['path_request'] = f"/section/{section_id}/add_theme/"
        user = user_by_session(self.request)
        if user is None:
            raise PermissionDenied()
        return context

    def post(self, request, *args, **kwargs):
        data = {'ok': False}
        section_form = SectionThemeForm(request.POST)
        user = user_by_session(self.request)

        if user is None or not user.is_admin:
            raise PermissionDenied()

        section_id_index = -3
        section_id = int(self.request.path.split('/')[section_id_index])
        if section_form.is_valid():
            try:
                section = Section.objects.get(id=section_id)
                Theme.objects.create(name=section_form.data['name'], datetime=timezone.now(),
                                     user=user, section=section)
                data['ok'] = True
            except BaseException as error:
                print(error)
        else:
            print('ooops')
        return JsonResponse(data)


class ThemePageView(TemplateView):
    template_name = 'theme.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_context(context, self.request)
        theme_id_index = -2
        theme_id = int(self.request.path.split('/')[theme_id_index])
        page = page_by_request(self.request)
        try:
            theme = Theme.objects.get(id=theme_id)
            context['theme_id'] = theme.id
            context['theme_name'] = theme.name
            context['section_id'] = theme.section.id
        except BaseException:
            raise PermissionDenied()

        context['page'] = page
        posts_by_page = 5
        width_paginator = 1
        posts = Post.objects.raw(f'select `id`, `user_id`, `is_edit`, `last_edit`, `text`, `datetime` '
                                  f'from `forum`.`post` where `post`.`theme_id` = {theme_id} '
                                   f'order by `datetime` limit {(page-1)*posts_by_page}, {posts_by_page}')

        number_posts = Post.objects.raw(f'select 1 as id, count(*) as cnt from `forum`.`post` where `post`.`theme_id` = {theme_id}')
        number_pages = 0
        if len(number_posts) == 1:
            number_pages = (number_posts[0].cnt // posts_by_page) + (1 if number_posts[0].cnt % posts_by_page > 0 else 0)
        context['number_pages'] = number_pages
        context['width_paginator'] = width_paginator
        context['window_pages'] = list(range(max(page-width_paginator, 2),
                                             min(page+width_paginator, number_pages-1)+1))
        context['page_path'] = f'/theme/{theme_id}/'

        context['posts'] = []
        for post in posts:
            data = {'id': post.id, 'user_id': post.user_id, 'is_edit': post.is_edit, 'last_edit': post.last_edit,
                    'text': post.text, 'datetime': post.datetime}
            user = User.objects.get(id=post.user_id)
            data['user_name'] = user.nickname
            context['posts'].append(data)

        return context

    def post(self, request, *args, **kwargs):
        theme_id_index = -2
        theme_id = int(self.request.path.split('/')[theme_id_index])
        user = user_by_session(self.request)
        data = {'ok': False}

        if user is None:
            raise PermissionDenied()

        if request.POST['is_add_post'] == 'true':
            limit_post_length = 500
            text_post = request.POST['post_text']
            if len(text_post) > limit_post_length and len(text_post) > 0:
                return JsonResponse(data)

            try:
                theme = Theme.objects.get(id=theme_id)
                Post.objects.create(text=text_post, is_edit=0, last_edit=None,
                                    user=user, theme=theme, datetime=timezone.now())
                data['ok'] = True
            except BaseException:
                raise PermissionDenied()
        elif request.POST['is_delete_post'] == 'true':
            if not user.is_admin:
                raise PermissionDenied()
            try:
                delete_post_id = request.POST['post_id']
                post = Post.objects.get(id=delete_post_id)
                post.delete()
                data['ok'] = True
            except BaseException:
                raise PermissionDenied()
        elif request.POST['is_edit_post'] == 'true':
            try:
                edit_post_id = request.POST['post_id']
                post = Post.objects.get(id=edit_post_id)
                if user.id != post.user.id:
                    raise PermissionDenied()
                post.text = request.POST['post_text']
                post.is_edit = 1
                post.last_edit = timezone.now()
                post.save(update_fields=['text', 'is_edit', 'last_edit'])
                data['ok'] = True
            except BaseException:
                raise PermissionDenied()
        elif request.POST['is_delete_theme'] == 'true':
            if not user.is_admin:
                raise PermissionDenied()
            try:
                theme = Theme.objects.get(id=theme_id)
                theme.delete()
                data['ok'] = True
            except BaseException:
                raise PermissionDenied()

        return JsonResponse(data)


class RegistrationPageView(FormView):
    template_name = 'registration.html'
    form_class = UserRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('is_confirm', '0') == '1':
            context['is_confirm'] = True
            context['message'] = 'Не удалось завершить регистрацию.'
            try:
                confirm_hash = self.request.GET['confirm_code']
                registration_form = RegistrationForm.objects.get(confirm_hash=confirm_hash)
                now = int(time.time())
                datetime_now = timezone.now()
                if len(User.objects.filter(nickname=registration_form.nickname)) == 0 and \
                len(User.objects.filter(email=registration_form.email)) == 0 and \
                    registration_form.time + REGISTRATION_CODE_TIME_LIFE >= now and registration_form.is_complete == 0:
                    User.objects.create(email=registration_form.email, nickname=registration_form.nickname,
                                        password_hash=registration_form.password_hash, is_admin=0,
                                        registration_date=datetime_now, last_activity=datetime_now)
                    registration_form.is_complete = 1
                    registration_form.save(update_fields=['is_complete'])
                    context['message'] = 'Регистрация завершена.'
            except BaseException:
                raise PermissionDenied()
        else:
            context['is_confirm'] = False

        return context

    def post(self, request, *args, **kwargs):
        data = {'ok': False, 'message': ''}
        registration_form = UserRegistrationForm(request.POST)

        if registration_form.is_valid() and len(User.objects.filter(nickname=registration_form.data['nickname'])) == 0 and \
                len(User.objects.filter(email=registration_form.data['email'])) == 0:
            password_hash = sha256(registration_form.data['password'].encode('utf-8')).hexdigest()
            now = int(time.time())
            confirm_hash = sha256((str(now) + registration_form.data['nickname'] + registration_form.data['password']
                                   + request.META['HTTP_USER_AGENT']).encode('utf-8')).hexdigest()
            RegistrationForm.objects.create(email=registration_form.data['email'],
                                            nickname=registration_form.data['nickname'],
                                            password_hash=password_hash, time=now, confirm_hash=confirm_hash,
                                            is_complete=0)
            data['ok'] = True
            link = f'http://{request.get_host()}/registration/?is_confirm=1&confirm_code={confirm_hash}'
            email = EmailMessage('Регистрация на форуме.',
                                 f'Для завершения регистрации пройдите по ссылке ниже:\n'
                                 f'{link}\n\n', to=[registration_form.data['email']])
            email.send()
        else:
            message = ''
            if len(User.objects.filter(nickname=registration_form.data['nickname'])) == 1:
                message = 'Данный псевдоним уже занят.'
            elif len(User.objects.filter(email=registration_form.data['email'])) == 1:
                message = 'Данный email уже используется.'
            elif not registration_form.is_valid():
                message = 'Форма заполнена не верно.'
            data['message'] = message

        return JsonResponse(data)
