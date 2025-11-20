# main/auth/Sign_up.py

import requests
from django.shortcuts import render, redirect 
from django.views.decorators.csrf import csrf_exempt

import hashlib  # ハッシュ化のためにインポート
import os       # ランダムなソルト生成のためにインポート

SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
SUPABASE_SIGNUP_URL = f"{SUPABASE_URL}/auth/v1/signup"
SUPABASE_DB_INSERT_URL = f"{SUPABASE_URL}/rest/v1/users" # public.users テーブルへのURL

# エラーメッセージを日本語に変換するロジック関数
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
        # メッセージ
        if "password should be at least 6 characters" in supabase_error_message_lower or \
             "password is too short" in supabase_error_message_lower:
            display_message = "パスワードが短すぎます。（最低6文字必要です）"
        elif "invalid email format" in supabase_error_message_lower or \
             "is invalid" in supabase_error_message_lower:
            display_message = "メールアドレスの形式が正しくありません。"
        elif "not found" in supabase_error_message_lower:
            display_message = "ユーザー登録に必要な情報が見つかりません。設定を確認してください。"
        # その他のAuthエラーがあればここに追加
    else:
        # DBエラー固有のメッセージハンドリング
        if "duplicate key value violates unique constraint" in supabase_error_message_lower:
            display_message = "このメールアドレスは既に登録されています。" # DB側での重複エラー
        elif "not found" in supabase_error_message_lower:
            display_message = "必要なデータが見つかりません。設定を確認してください。"
        elif "permission denied" in supabase_error_message_lower:
            display_message = "データベースへのアクセス権がありません。APIキーまたはポリシーを確認してください。"
        # その他のDBエラーがあればここに追加
    
    return display_message

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
                    "password": password,
                }
            )
            auth_response.raise_for_status()

            # ⭐ ユーザーIDの取得 ⭐
            auth_data = auth_response.json()
            # Auth登録成功時のレスポンス構造から、userオブジェクト内のIDを取得
            user_id = auth_data.get("user", {}).get("id") 
            
            if not user_id:
                 # IDが取得できない場合は処理を中止 (非常に稀)
                 raise ValueError("Supabase AuthからユーザーIDを取得できませんでした。")

            # Auth認証が成功した場合でも、public.usersテーブルに既にメールアドレスが存在するかチェック
            # これは、Supabase Authが既存ユーザーのサインアップ試行時にエラーを返さないセキュリティ挙動に対応するため
            check_db_url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}"
            check_db_response = requests.get(
                check_db_url,
                headers={
                    "apikey": SUPABASE_API_KEY,
                    "Authorization": f"Bearer {SUPABASE_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            check_db_response.raise_for_status()
            existing_users = check_db_response.json()

            if existing_users:
                # public.usersテーブルに既にこのメールアドレスが存在する場合
                return render(request, "auth/signup.html", {"message": "ユーザー登録エラー：このメールアドレスは既に登録されています。"})

        except requests.exceptions.HTTPError as e:
            # Authエラーにも日本語変換ロジックを適用
            display_message = get_translated_error_message(e, is_auth_error=True)
            return render(request, "auth/signup.html", {"message": f"ユーザー登録エラー：{display_message}"})
        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどを処理
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})


#ここからハッシュ化
        salt = os.urandom(16)
        
        iterations = 100000 
        
        hashed_password_bytes = hashlib.pbkdf2_hmac('sha256', 
                                                    password.encode('utf-8'), 
                                                    salt, 
                                                    iterations)
        
        combined_hash = f"pbkdf2_sha256${iterations}${salt.hex()}${hashed_password_bytes.hex()}"
#ここまでハッシュ化

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
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "password": combined_hash,
                    "is_admin_flag": 0
                }
            )
            # HTTPエラーを検出する（200番台でなければ例外を投げる）
            insert_response.raise_for_status()

            # 挿入結果を確認（Prefer: return=representation が有効なら挿入されたレコードが返る）
            try:
                created = insert_response.json()
            except ValueError:
                created = None

            # デバッグ: サーバが受け取った値を確認する
            print('Supabase insert response status:', insert_response.status_code)
            print('Supabase insert response body:', created)

            # created が存在し、is_admin_flag が明示的に設定されていない場合は警告
            if created:
                # PostgREST はリストで返すことが多いので対応
                rec = created[0] if isinstance(created, list) and len(created) > 0 else created
                if rec.get('is_admin_flag') is None:
                    print('Warning: is_admin_flag is NULL in returned record')

            return redirect('confirm_email')

        except requests.exceptions.HTTPError as e:
            # ★修正箇所：DB保存エラーにも日本語変換ロジックを適用（関数呼び出しに）★
            display_message = get_translated_error_message(e, is_auth_error=False)
            return render(request, "auth/signup.html", {"message": f"DB保存エラー：{display_message}"})
        except requests.exceptions.RequestException as e:
            # ネットワークエラーなどを処理
            return render(request, "auth/signup.html", {"message": f"ネットワークエラー：{str(e)}"})

    # POSTリクエストでない場合は、サインアップフォームを表示
    return render(request, "auth/signup.html")
