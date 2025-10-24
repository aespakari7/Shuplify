# C:\Admin\urls.py

from django.urls import path
from . import admin_top

urlpatterns = [
    path('top/', admin_top.admin_top, name='admin_top'),
    path('users/', admin_top.user_management, name='admin_users'),
    path('prompts/', admin_top.prompt_management, name='admin_prompts'),
]