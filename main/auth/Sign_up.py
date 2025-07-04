# main/auth/Sign_up.py

import requests
from django.shortcuts import render, redirect # redirect を忘れずにインポート
from django.views.decorators.csrf import csrf_exempt

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
SUPABASE_SIGNUP_URL = f"{SUPABASE_URL}/auth/v1/signup"
SUPABASE_DB_INSERT_URL = f"{SUPABASE_URL}/rest/v1/users"

@csrf_exempt
def signup(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")

        if not email or not password or not name:
            return render(request, "auth/signup.html", {"message": "メールアドレス、パスワード、名前は必須です。"})
        
        # 1. Supabase Auth でユーザー登録
        try:
            auth_response = requests.post(
                SUPABASE_SIGNUP_URL,
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "email": email,
                    "password": password
                }
            )

            auth_response.raise_for_status()

            auth_data = auth_response.json()
            print(f"Supabase Auth Response JSON: {auth_data}") # デバッグ用ログは残しておいても良いですが、最終的には削除してください

            # ★★★ ここを修正！ 'user' キーを探すのではなく、直接 'id' を取得します ★★★
            user_id = auth_data.get("id") # 直接 'id' キーの値を取得

            print(f"Extracted User ID: {user_id}") # デバッグ用ログ

            if not user_id:
                return render(request, "auth/signup.html", {"message": "ユーザーIDの取得に失敗しました。Supabase Authのレスポンスを確認してください。"})

        except requests.exceptions.HTTPError as e:
            error_details = e.response.json().get("msg", str(e))
            return render(request, "auth/signup.html", {"message": f"ユーザー登録エラー：{error_details}"})
        except requests.exceptions.RequestException as e:
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})


        try:
            insert_response = requests.post(
                SUPABASE_DB_INSERT_URL,
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Authorization": f"Bearer {SUPABASE_API_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                json={
                    "email": email,
                    "name": name,
                    "user_id": user_id,
                    "password": password
                }
            )
            insert_response.raise_for_status()

            # ★★★ 登録とDB保存が成功したら、ここからリダイレクトします ★★★
            return redirect('top') 

        except requests.exceptions.HTTPError as e:
            error_details = e.response.json().get("message", str(e))
            return render(request, "auth/signup.html", {"message": f"DB保存エラー：{error_details}"})
        except requests.exceptions.RequestException as e:
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})

    return render(request, "auth/signup.html")