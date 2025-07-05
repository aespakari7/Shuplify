# main/auth/Sign_up.py

import requests
from django.shortcuts import render, redirect 
from django.views.decorators.csrf import csrf_exempt

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
SUPABASE_SIGNUP_URL = f"{SUPABASE_URL}/auth/v1/signup"
SUPABASE_DB_INSERT_URL = f"{SUPABASE_URL}/rest/v1/users" # public.users テーブルへのURL

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
            # Authへのリクエストが200番台でなかったらエラーを発生させる
            auth_response.raise_for_status()

            # ここでSupabase Authへの登録は完了。AuthのUUIDは取得するが、
            # public.usersテーブルには保存しないため、変数に保持する必要はない。
            # 
            # もしデバッグのためにAuthのレスポンスを確認したい場合は、以下を残す
            # auth_data = auth_response.json()
            # print(f"Supabase Auth Response JSON: {auth_data}") 
            # 
            # また、AuthのIDをpublic.usersと紐付ける必要がなければ、user_idの取得とチェックは不要

        except requests.exceptions.HTTPError as e:
            # Supabase Authからのエラーレスポンスを処理
            error_details = e.response.json().get("msg", str(e))
            return render(request, "auth/signup.html", {"message": f"ユーザー登録エラー：{error_details}"})
        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどを処理
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})


        # 2. Supabase の 'users' テーブルにプロフィール情報を追加
        # 注: ここではパスワードやAuthのUUIDは送らない
        try:
            insert_response = requests.post(
                SUPABASE_DB_INSERT_URL,
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Authorization": f"Bearer {SUPABASE_API_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation" # 挿入したデータを返してもらう設定
                },
                json={
                    "email": email,
                    "name": name,
                    "password": password
                    # 'id' はDB側で自動採番されるので、ここでは送らない
                    # 'password' はセキュリティのためDBのusersテーブルには保存しない
                }
            )
            # usersテーブルへの挿入が200番台でなかったらエラーを発生させる
            insert_response.raise_for_status()

            # 登録とDB保存が成功したら、topページへリダイレクト
            return redirect('top') 

        except requests.exceptions.HTTPError as e:
            # public.usersテーブルへの挿入エラーを処理
            error_details = e.response.json().get("message", str(e))
            return render(request, "auth/signup.html", {"message": f"DB保存エラー：{error_details}"})
        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどを処理
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})

    # POSTリクエストでない場合は、サインアップフォームを表示
    return render(request, "auth/signup.html")