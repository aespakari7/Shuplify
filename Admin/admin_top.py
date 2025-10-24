# Admin/admin_top.py

from django.shortcuts import render

# ユーザー管理画面 (管理者ログイン後の開始画面)
def user_management(request):
    """
    ユーザー管理画面を表示する。
    テンプレート: Admin/admin_user.html
    """
    context = {
        'message': 'ユーザー管理画面',
        # 画面遷移の骨組みとして必要なダミーデータとURL名
        'users_list': ['User A', 'Admin X', 'User B'],
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_user.html', context)

# プロンプト管理画面
def prompt_management(request):
    """
    プロンプト管理画面を表示する。
    テンプレート: Admin/admin_prompt.html
    """
    context = {
        'message': 'プロンプト管理画面',
        # 画面遷移の骨組みとして必要なダミーデータとURL名
        'prompts_list': ['プロンプト1', 'プロンプト2'],
        'user_management_url': 'admin_users',
        'prompt_management_url': 'admin_prompts',
    }
    return render(request, 'Admin/admin_prompt.html', context)