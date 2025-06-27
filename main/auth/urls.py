# auth/urls.py
from django.urls import path
from . import Sign_up  # ← ビューがSign_up.pyならここ！

urlpatterns = [
    path('signup/', Sign_up.signup, name='signup'),  # /main/signup/ で実行
]