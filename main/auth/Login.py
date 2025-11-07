from django.shortcuts import render, redirect
import requests

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
SUPABASE_LOGIN_URL = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

def get_translated_error_message(e):
    try:
        error_json = e.response.json()
    except ValueError:
        error_json = {}

    msg = error_json.get("msg", error_json.get("message", error_json.get("error", str(e)))).lower()

    if "invalid login credentials" in msg:
        return "メールアドレスまたはパスワードが間違っています。"
    elif "email not confirmed" in msg:
        return "メールアドレスが確認されていません。"
    elif "password" in msg:
        return "パスワードが間違っています。"
    elif "invalid email" in msg:
        return "メールアドレスの形式が正しくありません。"
    return "ログインに失敗しました。入力内容を確認してください。"


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "auth/login.html", {"message": "メールアドレスとパスワードは必須です。"})

        try:
            response = requests.post(
                SUPABASE_LOGIN_URL,
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Content-Type": "application/json"
                },
                json={"email": email, "password": password}
            )
            response.raise_for_status()

            # ✅ Supabaseからのレスポンスを取得
            data = response.json()

            # ✅ セッションにユーザー情報を保存
            request.session["user"] = {
                "email": email,
                "access_token": data.get("access_token")
            }

            return redirect("top")

        except requests.exceptions.HTTPError as e:
            return render(request, "auth/login.html", {"message": get_translated_error_message(e)})

        except requests.exceptions.RequestException as e:
            return render(request, "auth/login.html", {"message": f"ネットワークエラー：{e}"})

    return render(request, "auth/login.html")


def top(request):
    user = request.session.get("user")
    if not user:
        return redirect("login")
    return render(request, "top.html", {"user": user})
