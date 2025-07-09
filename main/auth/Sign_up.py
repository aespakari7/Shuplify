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
        
# Supabase Auth認証機能
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

        except requests.exceptions.HTTPError as e:
            # Supabase Authからのエラーレスポンスを処理
            error_details = e.response.json().get("msg", str(e))
            return render(request, "auth/signup.html", {"message": f"ユーザー登録エラー：{error_details}"})
        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどを処理
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})


# Supabaseのusersテーブルに情報を追加
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
                    "password": password
                }
            )
            # usersテーブルへの挿入が200番台でなかったらエラーを発生させる
            insert_response.raise_for_status()

            # 登録とDB保存が成功したら、confirm_emailページへリダイレクト
            return redirect('confirm_email')

        except requests.exceptions.HTTPError as e:
            # public.usersテーブルへの挿入エラーを処理
            error_json = {}
            try:
                # SupabaseからのレスポンスをJSONとしてパース
                error_json = e.response.json()
            except ValueError: # JSONとしてパースできない場合
                pass

            # Supabaseのエラーメッセージを取得
            supabase_error_message = error_json.get("message", error_json.get("error", str(e)))
            supabase_error_message_lower = str(supabase_error_message).lower()#後で消す

            # ここでエラーメッセージを日本語に変換するロジックを追加
            display_message = "ユーザー情報の保存中に不明なエラーが発生しました。入力内容を確認してください。" # デフォルトメッセージ

            if "duplicate key value violates unique constraint" in supabase_error_message.lower(): # 小文字に変換して比較
                display_message = "このメールアドレスは既に登録されています。"
            elif "password is too short" in supabase_error_message_lower:
                display_message = "パスワードが短すぎます。（最低6文字必要です）"
            elif "invalid email format" in supabase_error_message_lower:
                display_message = "メールアドレスの形式が正しくありません。"
            elif "not found" in supabase_error_message_lower: # テーブル名の間違いや、アクセス権がない場合など
                display_message = "必要なデータが見つかりません。設定を確認してください。"

            return render(request, "auth/signup.html", {"message": f"DB保存エラー：{display_message}"})

        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどを処理
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})

    # POSTリクエストでない場合は、サインアップフォームを表示
    return render(request, "auth/signup.html")