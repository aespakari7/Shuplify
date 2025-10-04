# main/auth/Top.py

from django.shortcuts import render
from datetime import date
from .models import CalendarEvent, Company # モデルをインポート
from .utils import CalendarUtil
from django.contrib.auth.models import User # 仮のユーザー処理用

def top(request):
    # ユーザー認証が未実装のため、ダミー/暫定処理
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        # デバッグ/開発用: ログインしていない場合は、ダミーとしてID=1のユーザーを使用を試みる
        try:
            dummy_user = User.objects.first() 
            user_id = dummy_user.id if dummy_user else None
        except:
            pass # データベースが空の場合

    today = date.today()
    
    # 常に現在の月を表示
    year = today.year
    month = today.month

    # フィルタリング用のクエリセットを準備 (user_id があればフィルタ)
    if user_id is not None:
        # カレンダーに表示するイベントは、月全体の日付範囲でフィルタリングすると効率が良い
        # しかし、CalendarUtil内で日付ごとにフィルタリングするため、ここではユーザーIDのみで全イベントを取得
        all_events = CalendarEvent.objects.filter(user_id=user_id)
    else:
        all_events = CalendarEvent.objects.none()

    # 今日のイベントのみをフィルタリング
    today_events = all_events.filter(start_time__date=today).order_by('start_time')
    
    # CalendarUtilを使って月間カレンダーを生成
    cal = CalendarUtil(year, month)
    html_calendar = cal.format_month(all_events)

    context = {
        'current_month_name': today.strftime('%Y年%m月'),
        'html_calendar': html_calendar,
        'today_tasks': today_events,
        
        # URLを整理し、フロント側で使いやすいように変更
        'urls': {
            'profile': '/profile/',
            'chat': '/main/auth/aichat/',
            'es_tutor': '/main/auth/es-tutor/',
            'email_tutor': '/main/auth/email-tutor/',
            'self_analysis': '/self-analysis/',
            # CalendarDetailのURLはCalendarUtilでイベントIDを使って生成済み
        }
    }

    return render(request, 'auth/top.html', context)