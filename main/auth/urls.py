# main/auth/urls.py

from django.urls import path
from . import Sign_up
#from . import Login
from . import Top
from . import AIchat
from django.views.generic import TemplateView

urlpatterns = [
    path('signup/', Sign_up.signup, name='signup'), # /main/auth/signup/ で実行される
    #path('signup/', Login.login, name='signup'), # /main/auth/login/ で実行される
    path('top/', Top.top, name='top'), # /main/auth/top/ で実行される
    path('confirm-email/', TemplateView.as_view(template_name='auth/confirm_email.html'), name='confirm_email'),
    path('aichat/', AIchat.aichat, name='aichat'),
]