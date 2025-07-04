# main/auth/Top.py

from django.shortcuts import render

def top(request):
    """
    top.html を表示するビュー関数
    """
    return render(request, 'auth/top.html') # top.html のパスを指定