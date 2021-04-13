"""forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('login/', include('pages.urls')),
    path('exit/', include('pages.urls')),
    path('add_section/', include('pages.urls')),
    re_path(r'^section/\d+/$', include('pages.urls')),
    re_path(r'^section/\d+/add_theme/$', include('pages.urls')),
    re_path(r'^theme/\d+/$', include('pages.urls')),
    re_path(r'^favicon\.ico$', include('pages.urls')),
    path('registration/', include('pages.urls')),
]
