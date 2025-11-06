# Admin/admin_top.py

from django.shortcuts import render, redirect
import requests

# -----------------------------------------------------------------
# Supabase接続情報
# -----------------------------------------------------------------
SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTU1MDkxOSwiZXhwIjoyMDYxMTI2OTE5fQ.Mb2UMHZJSYPcXDujxs4q0Dgvh7tXh38EJpPooqydkZs"
SUPABASE_DB_URL_USERS = f"{SUPABASE_URL}/rest/v1/users" 
SUPABASE_DB_URL_PROMPTS = f"{SUPABASE_URL}/rest/v1/prompts"

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
    all_users = []
    admin_users_list = []  # 管理者リスト
    general_users_list = [] # 一般ユーザーリスト
    
    try:
        # requests.get を使用してデータを取得 (idとnameのみを選択)
        response = requests.get(
            f"{SUPABASE_DB_URL_USERS}?select=user_id,name,is_admin_flag", 
            headers={
                "apikey": SUPABASE_API_KEY, 
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
            }
        )
        response.raise_for_status() 
        
        all_users = response.json()
        
        for user in all_users:
            # Supabaseの真偽値は数値(1/0)またはブール値(true/false)で返されます。
            # ここでは数値の 1 を管理者と仮定します。
            if user.get('is_admin_flag') == 1 or user.get('is_admin_flag') is True:
                admin_users_list.append(user)
            else:
                general_users_list.append(user)

    except requests.exceptions.RequestException as e:
        print(f"Supabaseからのデータ取得中にエラーが発生しました: {e}")
        try:
            print(f"Supabase詳細エラー: {response.text}") # サーバーから返された具体的なエラーメッセージ
        except:
            pass
        users_list = []
        
    context = {
        'message': 'ユーザー管理画面',
        'admin_users': admin_users_list,     # 管理者ユーザーリスト
        'general_users': general_users_list, # 一般ユーザーリスト
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
                    f"{SUPABASE_DB_URL_USERS}?user_id=eq.{user_id}", # idがuser_idに等しいレコードを削除
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
    context = {}
    # ES用とメール用のプロンプトタイトルを定義
    PROMPT_TITLES = ['ES添削用', 'メール添削用']
    
    # POSTリクエスト（更新処理）
    if request.method == 'POST':
        prompt_title = request.POST.get('title')
        new_content = request.POST.get('content')
        
        if prompt_title in PROMPT_TITLES and new_content is not None:
            try:
                # SupabaseにPATCHリクエストを送信してプロンプトを更新
                update_response = requests.patch(
                    f"{SUPABASE_DB_URL_PROMPTS}?title=eq.{prompt_title}",
                    headers={
                        "apikey": SUPABASE_API_KEY,
                        "Authorization": f"Bearer {SUPABASE_API_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation", # 更新されたレコードを返す
                    },
                    json={"content": new_content}
                )
                update_response.raise_for_status()
                
                context = {'message': f"✅ '{prompt_title}' のプロンプトを更新しました。", 'success': True}
                # 更新後、GET処理に進み最新のデータを取得
            
            except requests.exceptions.RequestException as e:
                error_detail = update_response.text if 'update_response' in locals() else str(e)
                print(f"Supabaseでのプロンプト更新中にエラーが発生しました: {error_detail}")
                context = {'message': f"❌ 更新エラー: {error_detail}", 'error': True}
                # エラーの場合は次のGET処理に進まず、エラーメッセージを表示
                return render(request, 'Admin/admin_prompt.html', context)


    # GETリクエスト（データ取得と表示）
    
    # 既存のプロンプトデータを取得
    prompts_data = {}
    
    try:
        # すべてのプロンプトデータを取得
        response = requests.get(
            f"{SUPABASE_DB_URL_PROMPTS}?select=title,content", 
            headers={
                "apikey": SUPABASE_API_KEY, 
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
            }
        )
        response.raise_for_status()
        
        data = response.json()
        
        # 取得したデータをタイトルをキーとする辞書に変換
        for item in data:
            prompts_data[item['title']] = item['content']
            
    except requests.exceptions.RequestException as e:
        error_detail = response.text if 'response' in locals() else str(e)
        print(f"Supabaseからのプロンプト取得中にエラーが発生しました: {error_detail}")
        context = {
            'message': '❌ データ取得エラーが発生しました。', 
            'error': True,
            'user_management_url': 'admin_users',
            'prompt_management_url': 'admin_prompts',
        }
        return render(request, 'Admin/admin_prompt.html', context)

    
    # テンプレートに渡すコンテキストを作成
    context = {
        'message': context.get('message', '変更なし'), 
        'error': context.get('error', False),
        'success': context.get('success', False),
        'es_prompt': prompts_data.get('ES添削用', 'プロンプトがデータベースに見つかりません。'),
        'email_prompt': prompts_data.get('メール添削用', 'プロンプトがデータベースに見つかりません。'),
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_prompt.html', context)