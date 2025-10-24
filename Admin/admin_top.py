# Admin/admin_top.py

from django.shortcuts import render

# ユーザー管理画面 (管理者ログイン後の開始画面)
def user_management(request):
    """ユーザー管理画面を表示"""
    # templates/Admin/admin_user.html を参照
    context = {
        'message': 'ユーザー管理画面',
        'users_list': ['User A', 'Admin X', 'User B'],
        # リダイレクト先として、自分自身（admin_users）とプロンプト管理（admin_prompts）のURL名を渡す
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_user.html', context)

# プロンプト管理画面
def prompt_management(request):
    """プロンプト管理画面を表示"""
    # templates/Admin/admin_prompt.html を参照
    context = {
        'message': 'プロンプト管理画面',
        'prompts_list': ['プロンプト1', 'プロンプト2'],
        # ナビゲーション用にURL名を渡す
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_prompt.html', context)