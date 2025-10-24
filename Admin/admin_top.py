# Admin/admin_top.py

from django.shortcuts import render, redirect
from supabase import create_client, Client

SUPABASE_URL = 'https://uzoblakkftugdweloxku.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTA5MTksImV4cCI6MjA2MTEyNjkxOX0.l-CxOBeAyh1mYcJYaZR8Jh9NryPFoWPiYwYB0sl4bc0'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# 管理者トップ画面
def admin_top(request):
    context = {
        'message': '管理者TOPページへようこそ！',
        'user_management_url': 'admin_users',    # ユーザー管理画面へのURL名
        'prompt_management_url': 'admin_prompts',  # プロンプト管理画面へのURL名
    }
    return render(request, 'Admin/admin_top.html', context)


# ユーザー管理画面 
def user_management(request):
    """
    Supabaseの 'users' テーブルからユーザー一覧を取得し、表示する。
    """
    try:
        response = supabase.table('users').select('id, name').execute()
        
        users_list = response.data
        
    except Exception as e:
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
                # ユーザーIDをキーにして削除
                supabase.table('users').delete().eq('id', user_id).execute()
                print(f"ユーザーID: {user_id} のアカウントをSupabaseから削除しました。")
            except Exception as e:
                print(f"Supabaseでの削除中にエラーが発生しました: {e}")
        
        # 処理後、ユーザー一覧画面に戻る
        return redirect('admin_users')
    
    return redirect('admin_users')


# プロンプト管理画面
def prompt_management(request):
    context = {
        'message': 'プロンプト管理画面',
        'prompts_list': ['プロンプト1', 'プロンプト2'],
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_prompt.html', context)