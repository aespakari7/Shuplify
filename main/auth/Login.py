import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
SUPABASE_LOGIN_URL = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"


# --- エラーメッセージ翻訳 ---
def get_translated_error_message(response_json):
    msg = response_json.get("msg") or response_json.get("message") or response_json.get("error", "")
    msg_lower = msg.lower()

    if "invalid login credentials" in msg_lower:
        return "メールアドレスまたはパスワードが間違っています。"
    elif "email not confirmed" in msg_lower:
        return "メールアドレスが確認されていません。受信メールを確認してください。"
    elif "password" in msg_lower:
        return "パスワードが間違っています。"
    elif "invalid email" in msg_lower:
        return "メールアドレスの形式が正しくありません。"
    else:
        return "ログインに失敗しました。入力内容を確認してください。"


# --- CSRF保護有効（安全） ---
@csrf_protect
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "auth/login.html", {"message": "メールアドレスとパスワードは必須です。"})

        # Supabase Auth ログイン処理
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

        # --- ステータスコード確認 ---
        if login_response.status_code == 200:
            data = login_response.json()
            if "access_token" in data:
                # ✅ ログイン成功時
                request.session["user_email"] = email  # セッションに保存（任意）
                return redirect("top")

        # ❌ ログイン失敗時
        try:
            error_json = login_response.json()
        except Exception:
            error_json = {}

        display_message = get_translated_error_message(error_json)
        return render(request, "auth/login.html", {"message": f"ログインエラー：{display_message}"})

    # --- GETメソッド（ログイン画面表示） ---
    return render(request, "auth/login.html")
