# C:\Admin\views.py

from django.shortcuts import render

# Admin/admin_top.html を参照
def admin_top(request):
    return render(request, 'Admin/admin_top.html', {'message': 'ようこそ、管理者様！'})

# ... (user_management, prompt_management もここに定義) ...