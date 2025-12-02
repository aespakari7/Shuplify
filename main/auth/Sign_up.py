# main/auth/Sign_up.py

import requests
from django.shortcuts import render, redirect 
from django.views.decorators.csrf import csrf_exempt
import hashlib
import os

# -----------------------------------------------------------------
# 設定
# -----------------------------------------------------------------
SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
# クライアント（ブラウザ）向け公開キー（Auth認証に使用）
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
# サーバー向け管理者キー（DB操作に使用）
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTU1MDkxOSwiZXhwIjoyMDYxMTI2OTE5fQ.Mb2UMHZJSYPcXDujxs4q0Dgvh7tXh38EJpPooqydkZs" # ⭐ 追加したService Key ⭐

SUPABASE_SIGNUP_URL = f"{SUPABASE_URL}/auth/v1/signup"
SUPABASE_DB_INSERT_URL = f"{SUPABASE_URL}/rest/v1/users" # public.users テーブルへのURL

# -----------------------------------------------------------------
# エラーメッセージ変換関数
# -----------------------------------------------------------------
def get_translated_error_message(e, is_auth_error=True):
    error_json = {}
    try:
        error_json = e.response.json()
    except ValueError:
        pass

    # Supabaseからのエラーメッセージを取得
    if is_auth_error:
        supabase_error_message = error_json.get("msg", error_json.get("message", error_json.get("error", str(e))))
    else: # DBエラーの場合
        supabase_error_message = error_json.get("message", error_json.get("error", str(e)))
        
    supabase_error_message_lower = str(supabase_error_message).lower()

    display_message = "不明なエラーが発生しました。入力内容を確認してください。"

    # 日本語変換ロジック
    if is_auth_error:
        if "password should be at least 6 characters" in supabase_error_message_lower or \
             "password is too short" in supabase_error_message_lower:
            display_message = "パスワードが短すぎます。（最低6文字必要です）"
        elif "invalid email format" in supabase_error_message_lower or \
             "is invalid" in supabase_error_message_lower:
            display_message = "メールアドレスの形式が正しくありません。"
        elif "not found" in supabase_error_message_lower:
            display_message = "ユーザー登録に必要な情報が見つかりません。設定を確認してください。"
    else:
        # DBエラー固有のメッセージハンドリング
        if "duplicate key value violates unique constraint" in supabase_error_message_lower:
            display_message = "このメールアドレスは既に登録されています。"
        elif "not found" in supabase_error_message_lower:
            display_message = "必要なデータが見つかりません。設定を確認してください。"
        elif "permission denied" in supabase_error_message_lower:
            display_message = "データベースへのアクセス権がありません。APIキーまたはポリシーを確認してください。"
    
    return display_message

# -----------------------------------------------------------------
# サインアップ ビュー関数
# -----------------------------------------------------------------
@csrf_exempt
def signup(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")

        if not email or not password or not name:
            return render(request, "auth/signup.html", {"message": "メールアドレス、パスワード、名前は必須です。"})
        
        # ---------------------------------------------------------
        # 1. Supabase Auth認証機能 (Anon Keyを使用)
        # ---------------------------------------------------------
        try:
            auth_response = requests.post(
                SUPABASE_SIGNUP_URL,
                headers={
                    "apikey": SUPABASE_API_KEY, # AuthはAnon KeyでOK
                    "Content-Type": "application/json"
                },
                json={
                    "email": email,
                    "password": password,
                }
            )
            auth_response.raise_for_status()

            # ⭐ ユーザーIDの取得 ⭐
            auth_data = auth_response.json()
            user_id = auth_data.get("id")

            if not user_id:
                raise ValueError("Supabase AuthからユーザーIDを取得できませんでした。")

            # ---------------------------------------------------------
            # 2. DB重複チェック (念の為) - ⭐ Service Keyに変更 ⭐
            # ---------------------------------------------------------
            check_db_url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}"
            check_db_response = requests.get(
                check_db_url,
                headers={
                    "apikey": SUPABASE_SERVICE_KEY, # ⭐ 修正 ⭐
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", # ⭐ 修正 ⭐
                    "Content-Type": "application/json"
                }
            )
            check_db_response.raise_for_status()
            existing_users = check_db_response.json()

            if existing_users:
                return render(request, "auth/signup.html", {"message": "ユーザー登録エラー：このメールアドレスは既に登録されています。"})

        except requests.exceptions.HTTPError as e:
            display_message = get_translated_error_message(e, is_auth_error=True)
            return render(request, "auth/signup.html", {"message": f"ユーザー登録エラー：{display_message}"})
        except requests.exceptions.RequestException as e:
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})
        except ValueError as e:
            return render(request, "auth/signup.html", {"message": f"システムエラー：{str(e)}"})


        # ---------------------------------------------------------
        # 3. DB保存用パスワードのハッシュ化
        # ---------------------------------------------------------
        salt = os.urandom(16)
        iterations = 100000 
        
        hashed_password_bytes = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt, 
            iterations
        )
        
        combined_hash = f"pbkdf2_sha256${iterations}${salt.hex()}${hashed_password_bytes.hex()}"

        # ---------------------------------------------------------
        # 4. Supabaseのusersテーブルに情報を追加 (Service Role Keyを使用)
        # ---------------------------------------------------------
        try:
            insert_response = requests.post(
                SUPABASE_DB_INSERT_URL,
                headers={
                    "apikey": SUPABASE_SERVICE_KEY, # ⭐ 修正：Service Role Keyを使用 ⭐
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}", # ⭐ 修正：Service Role Keyを使用 ⭐
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                json={
                    "user_id": user_id, 
                    "email": email,
                    "name": name,
                    "password": combined_hash, 
                    "is_admin_flag": 0
                }
            )
            insert_response.raise_for_status()

            # 挿入結果を確認
            try:
                created = insert_response.json()
            except ValueError:
                created = None

            print('Supabase insert response status:', insert_response.status_code)
            
            if created:
                rec = created[0] if isinstance(created, list) and len(created) > 0 else created
                if rec.get('is_admin_flag') is None:
                    print('Warning: is_admin_flag is NULL in returned record')

            return redirect('confirm_email')

        except requests.exceptions.HTTPError as e:
            try:
                raw_error = e.response.json()
            except:
                raw_error = e.response.text
            
            # コンソール（ターミナル）に出力
            print(f"DEBUG - Supabase DB Insert Error: {raw_error}")
            return render(request, "auth/signup.html", {"message": f"DB保存エラー(DEBUG): {raw_error}"})
        except requests.exceptions.RequestException as e:
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})

    # POSTリクエストでない場合は、サインアップフォームを表示
    return render(request, "auth/signup.html")