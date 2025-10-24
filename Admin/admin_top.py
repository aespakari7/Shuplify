# Admin/admin_top.py

from django.shortcuts import render, redirect
import requests

# -----------------------------------------------------------------
# Supabase接続情報
# -----------------------------------------------------------------
SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0"
SUPABASE_DB_URL = f"{SUPABASE_URL}/rest/v1/users" # public.users テーブルへのURL


# -----------------------------------------------------------------
# 管理者トップ画面
# -----------------------------------------------------------------
def admin_top(request):
    context = {
        'message': '管理者TOPページへようこそ！',
        'user_management_url': 'admin_users',    # ユーザー管理画面へのURL名
        'prompt_management_url': 'admin_prompts',  # プロンプト管理画面へのURL名
    }
    return render(request, 'Admin/admin_top.html', context)


# -----------------------------------------------------------------
# ユーザー管理画面 
# -----------------------------------------------------------------
def user_management(request):
    """
    Supabaseの 'users' テーブルからユーザー一覧を取得し、表示する。
    """
    users_list = []
    
    try:
        # requests.get を使用してデータを取得 (idとnameのみを選択)
        response = requests.get(
            f"{SUPABASE_DB_URL}?select=id,name", 
            headers={
                "apikey": SUPABASE_API_KEY,
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
            }
        )
        response.raise_for_status() # HTTPエラーチェック
        
        users_list = response.json() # JSONレスポンスをリストとして取得
        
    except requests.exceptions.RequestException as e:
        print(f"Supabaseからのデータ取得中にエラーが発生しました: {e}")
        users_list = []
        
    context = {
        'message': 'ユーザー管理画面',
        'users_list': users_list,
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_user.html', context)

# ユーザー削除処理
def delete_user(request):

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        if user_id:
            try:
                # requests.delete を使用してレコードを削除
                delete_response = requests.delete(
                    f"{SUPABASE_DB_URL}?id=eq.{user_id}", # idがuser_idに等しいレコードを削除
                    headers={
                        "apikey": SUPABASE_API_KEY,
                        "Authorization": f"Bearer {SUPABASE_API_KEY}",
                    }
                )
                delete_response.raise_for_status() # HTTPエラーチェック
                
                print(f"ユーザーID: {user_id} のアカウントをSupabaseから削除しました。")
                
            except requests.exceptions.RequestException as e:
                print(f"Supabaseでの削除中にエラーが発生しました: {e}")
        
        # 処理後、ユーザー一覧画面に戻る
        return redirect('admin_users')
    
    return redirect('admin_users')


# -----------------------------------------------------------------
# プロンプト管理画面
# -----------------------------------------------------------------
def prompt_management(request):
    context = {
        'message': 'プロンプト管理画面',
        'prompts_list': ['プロンプト1', 'プロンプト2'],
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_prompt.html', context)