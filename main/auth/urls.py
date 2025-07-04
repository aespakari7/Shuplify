# main/auth/urls.py

from django.urls import path
from . import Sign_up
from . import Top # ★ Top.py から top 関数をインポート

urlpatterns = [
    path('signup/', Sign_up.signup, name='signup'), # /main/auth/signup/ で実行される
    path('top/', Top.top, name='top'),             # /main/auth/top/ で実行される
]