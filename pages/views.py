# pages/views.py
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from hashlib import sha256
import time
from .models import User, Session, Section, Theme, Post
from .form import LoginForm, SectionThemeForm
from django.utils import timezone


SESSION_TIME_LENGTH = 60*60*24


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
            context['section_id'] = Section.objects.get(id=section_id).id
        except BaseException:
            raise PermissionDenied()
        context['page'] = page
        themes_by_page = 5

        themes = Theme.objects.raw(f'select id, name, time, cnt from '
                                   f'(select tb1.`id`, tb1.`name`, max(tb2.`datetime`) as time, count(tb2.`id`) as cnt '
                                   f'from `forum`.`theme` as tb1 left join `forum`.`post` as tb2 on tb1.id = tb2.theme_id '
                                   f'where tb1.section_id = {context["section_id"]}) as tb '
                                   f'order by time desc limit {(page-1)*themes_by_page}, {themes_by_page}')
        context['themes'] = []
        for theme in themes:
            if theme.id is None:
                break
            data = {'id': theme.id, 'name': theme.name, 'number_posts': theme.cnt, 'date_last_post': theme.time}
            data['date_last_post'] = data['date_last_post'] if data['date_last_post'] is not None else 'Нет сообщений'
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
        context['section_id'] = int(self.request.path.split('/')[-3])
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
                Theme.objects.create(name=section_form.data['name'], user=user, section=section)
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
        except BaseException:
            raise PermissionDenied()
        context['page'] = page
        posts_by_page = 5

        posts = Post.objects.raw(f'select `id`, `user_id`, `is_edit`, `last_edit`, `text`, `datetime` '
                                  f'from `forum`.`post` where `post`.`theme_id` = {context["theme_id"]} '
                                   f'order by `datetime` limit {(page-1)*posts_by_page}, {posts_by_page}')
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



