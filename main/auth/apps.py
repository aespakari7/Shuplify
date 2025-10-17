# C:\main\auth\apps.py

from django.apps import AppConfig

class MainAuthConfig(AppConfig):
    # Django 4.x 以降の推奨設定
    default_auto_field = 'django.db.models.BigAutoField'
    # アプリケーションのPythonパス
    name = 'main.auth' 
    # ★★★ 競合しないユニークなラベルを設定 ★★★
    label = 'shuplify_auth_app' 
    # または 'main_auth' など、重複しない名前であれば何でもOKです