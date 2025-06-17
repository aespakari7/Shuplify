import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"  # ← 本番運用では.envで管理してください
SUPABASE_SIGNUP_URL = f"{SUPABASE_URL}/auth/v1/signup"
SUPABASE_DB_INSERT_URL = f"{SUPABASE_URL}/rest/v1/users"

@csrf_exempt  # フォームから直接POSTするなら必要（セキュリティ対策は後で強化）
def signup(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")

        # 1. Supabase Auth でユーザー登録
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

        if auth_response.status_code not in [200, 201]:
            return render(request, "signup.html", {"message": f"登録エラー：{auth_response.json()}"})

        user_id = auth_response.json().get("user", {}).get("id")

        # 2. Supabase の 'users' テーブルに追加
        insert_response = requests.post(
            SUPABASE_DB_INSERT_URL,
            headers={
                "apikey": SUPABASE_API_KEY,
                "Authorization": f"Bearer {SUPABASE_API_KEY}",  # ← anonキーでOK
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json={
                "email": email,
                "name": name,
                "user_id": user_id
            }
        )

        if insert_response.status_code not in [200, 201]:
            return render(request, "signup.html", {"message": f"DB保存エラー：{insert_response.json()}"})

        return render(request, "signup.html", {"message": "登録完了しました！"})

    return render(request, "signup.html")
