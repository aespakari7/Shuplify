# main/auth/Top.py

from django.shortcuts import render
from datetime import date
from .models import CalendarEvent # Companyのインポートは不要
from .utils import CalendarUtil
from django.contrib.auth.models import User 

def top(request):
    # ユーザー認証が未実装のため、ダミー/暫定処理
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        # デバッグ/開発用: ログインしていない場合は、ダミーとしてID=1のユーザーを使用を試みる
        try:
            # 実際の環境に合わせて User の取得ロジックを調整してください
            dummy_user = User.objects.first() 
            user_id = dummy_user.id if dummy_user else 1 # 暫定的にID=1
        except:
            user_id = 1 

    today = date.today()
    year = today.year
    month = today.month
    
    # フィルタリング用のクエリセットを準備
    if user_id is not None:
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
        'today_tasks': today_events, # 生のイベントオブジェクトをそのまま渡す
        
        # URLを整理
        'urls': {
            'profile': '/profile/',
            'chat': '/main/auth/aichat/', 
            'es_tutor': '/main/auth/es-tutor/',
            'email_tutor': '/main/auth/email-tutor/',
            'self_analysis': '/self-analysis/',
        }
    }

    return render(request, 'auth/top.html', context)