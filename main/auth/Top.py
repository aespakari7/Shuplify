# main/auth/Top.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required # ログイン必須にするため
from datetime import date
# 同じディレクトリ内の models.py から CalendarEvent をインポート
from .models import CalendarEvent 

@login_required 
def top(request):
    """
    ユーザーのTOPページを表示し、今日のタスクをデータベースから取得して渡すビュー
    """
    user_id = request.user.id
    today = date.today()

    # 現在のユーザーに紐づく今日のカレンダーイベントを取得
    today_events = CalendarEvent.objects.filter(
        user_id=user_id,
        start_time__date=today
    ).order_by('start_time')

    # テンプレートに渡すコンテキストデータ
    context = {
        'today_tasks': today_events,
        'profile_url': '/profile/', # 仮のURL、実際のURLパスに合わせて修正してください
        'chat_url': '/chat/',
        'self_analysis_url': '/self-analysis/',
        'calendar_detail_url': '/calendar-detail/',
        'es_edit_url': '/es-edit/',
        'company_analysis_url': '/company-analysis/',
        'mail_edit_url': '/mail-edit/',
        'company_manage_url': '/company-manage/',
    }

    # 'main/auth/templates/auth/top.html' をレンダリング
    return render(request, 'auth/top.html', context)