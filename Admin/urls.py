# C:\Admin\urls.py

from django.urls import path
from . import views # Admin/views.py をインポート

urlpatterns = [
    # /admin/top/ にアクセス
    path('top/', views.admin_top, name='admin_top'), 
    
    # /admin/users/ にアクセス
    path('users/', views.user_management, name='user_management'),
    
    # /admin/prompts/ にアクセス
    path('prompts/', views.prompt_management, name='prompt_management'),
]