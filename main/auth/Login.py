<<<<<<< HEAD
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # ← ここが必要
]


from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    error_message = None  # 初期値はエラーなし
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
       
        if email != "test@example.com" or password != "pass123":
            error_message = "メールアドレスまたはパスワードが間違っています"
        else:
            return redirect('home')  # 成功時はリダイレクト

    return render(request, 'login.html', {'error': error_message})
=======
# main/auth/Login.py

import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = ""
SUPABASE_LOGIN_URL = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

# エラーメッセージ翻訳
def get_translated_error_message(e):
    error_json = {}
    try:
        error_json = e.response.json()
    except ValueError:
        pass

    supabase_error_message = error_json.get("msg", error_json.get("message", error_json.get("error", str(e))))
    supabase_error_message_lower = str(supabase_error_message).lower()

    display_message = "ログインに失敗しました。入力内容を確認してください。"

    if "invalid login credentials" in supabase_error_message_lower:
        display_message = "メールアドレスまたはパスワードが間違っています。"
    elif "email not confirmed" in supabase_error_message_lower:
        display_message = "メールアドレスが確認されていません。受信したメールを確認してください。"
    elif "password" in supabase_error_message_lower:
        display_message = "パスワードが間違っています。"
    elif "invalid email" in supabase_error_message_lower:
        display_message = "メールアドレスの形式が正しくありません。"

    return display_message


@csrf_exempt
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "auth/login.html", {"message": "メールアドレスとパスワードは必須です。"})

        # Supabase Authログイン
        try:
            login_response = requests.post(
                SUPABASE_LOGIN_URL,
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "email": email,
                    "password": password
                }
            )
            login_response.raise_for_status()

            # ログイン成功 → トップページへ
            return redirect("top")

        except requests.exceptions.HTTPError as e:
            display_message = get_translated_error_message(e)
            return render(request, "auth/login.html", {"message": f"ログインエラー：{display_message}"})
        except requests.exceptions.RequestException as e:
            return render(request, "auth/login.html", {"message": f"ネットワークエラー：{str(e)}"})

    # GETリクエスト時はログイン画面を表示
    return render(request, "auth/login.html")
>>>>>>> main
