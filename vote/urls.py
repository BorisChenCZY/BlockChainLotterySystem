"""vote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, re_path

import startvote.views as v1

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', v1.index),
    re_path(r'^article/(?P<id>[0-9]+)$', v1.article_page, name="article_page"),
    re_path(r'^edit/(?P<id>[0-9]+)$', v1.edit_page,name='edit_page'),
    re_path(r'^edit/action$', v1.edit_action,name='edit_action'),
    re_path(r'hello', v1.hello)
]
