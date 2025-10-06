# main/auth/Top.py

from django.shortcuts import render, redirect
from datetime import date , datetime
from .models import CalendarEvent
from .utils import CalendarUtil
from django.contrib.auth.models import User 

def top(request):

    # セッションがまだなので仮 user_id 5 でログインしてる事にする
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        try:
            dummy_user = User.objects.first() 
            user_id = dummy_user.id if dummy_user else 5
        except:
            user_id = 5
    #ここまで仮

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
    
    # 月間カレンダーを生成
    cal = CalendarUtil(year, month)
    html_calendar = cal.format_month(all_events)

    context = {
        'current_month_name': today.strftime('%Y年%m月'),
        'html_calendar': html_calendar,
        'today_tasks': today_events, # 生のイベントオブジェクトをそのまま渡す
        
        # URLを整理
        'urls': {
            'es_tutor': '/main/auth/es-tutor/',
            'email_tutor': '/main/auth/email-tutor/',
        }
    }

    return render(request, 'auth/top.html', context)

def add_event(request):
    """ イベント追加フォームの表示とデータ保存を処理 """
    
    # ユーザーIDを取得 (イベント保存に必要)
    user_id = get_current_user_id(request)

    if user_id is None:
        # ユーザーIDが特定できない場合はログインページなどにリダイレクト（ここではTOPへ）
        return redirect('top')

    if request.method == 'POST':
        # フォームが送信されたときの処理
        
        # POSTデータから各フィールドを取得
        title = request.POST.get('title')
        memo = request.POST.get('memo')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        
        # 日付と時刻を結合して datetime オブジェクトにする
        if start_date and start_time:
            start_datetime_str = f"{start_date} {start_time}"
            # datetime.strptimeで文字列をDateTimeフィールドに合うように変換
            try:
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
            except ValueError:
                # 日時形式が不正な場合はTOPへ戻す
                return redirect('top') 
        else:
            # 必須項目がない場合はTOPへ戻す
            return redirect('top') 

        # データベースに保存
        CalendarEvent.objects.create(
            user_id=user_id,
            title=title,
            memo=memo,
            start_time=start_datetime,
            # end_timeはnull許容なので省略
        )
        
        # 登録後、TOPページへリダイレクト
        return redirect('top')
    
    else:
        # GETリクエストの場合（フォーム表示）
        context = {
            'today_date': date.today().strftime('%Y-%m-%d') # フォームの初期値用に今日の日付を渡す
        }
        return render(request, 'auth/add_event.html', context)