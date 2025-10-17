# main/auth/Top.py

from django.shortcuts import render, redirect, get_object_or_404 # get_object_or_404 を追加
from datetime import date, datetime, timedelta
from .models import CalendarEvent
from .utils import CalendarUtil
from django.contrib.auth.models import User 


# -----------------------------------------------------------------
# ヘルパー関数: ユーザーIDの取得
# -----------------------------------------------------------------
def get_current_user_id(request):
    """ ログイン状態に応じてuser_idを決定するヘルパー関数 """
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        # デバッグ/開発用: ログインしていない場合は、データ投入済みのID=5を使用
        try:
            # データベースにユーザーがいればそのIDを使う
            dummy_user = User.objects.first() 
            user_id = dummy_user.id if dummy_user else 5
        except:
            # DBにアクセスできなかった場合
            user_id = 5
    return user_id


# -----------------------------------------------------------------
# ビュー: TOPページ (カレンダー表示)
# -----------------------------------------------------------------
def top(request):
    """ 
    TOPページの表示（カレンダーと今日のタスク）。
    URLパラメータ (year, month) に基づいて表示月を切り替える。
    """
    
    user_id = get_current_user_id(request)

    # ----------------------------------------------------
    # ★表示する年月の決定ロジック
    # ----------------------------------------------------
    today = date.today()
    
    # デフォルトは今日の日付
    current_year = today.year
    current_month = today.month

    # URLパラメータから年と月を取得し、あれば上書き
    year_str = request.GET.get('year')
    month_str = request.GET.get('month')
    
    try:
        if year_str and month_str:
            current_year = int(year_str)
            current_month = int(month_str)
    except ValueError:
        pass # パラメータが無効な場合は現在の年月を使用
        
    # カレンダーの表示月（1日を設定）
    current_date = date(current_year, current_month, 1)

    # ----------------------------------------------------
    # ★ナビゲーション月の計算
    # ----------------------------------------------------
    
    # 前月（< ボタン）の計算
    prev_month = current_month - 1
    prev_year = current_year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    # 次月（> ボタン）の計算
    next_month = current_month + 1
    next_year = current_year
    if next_month == 13:
        next_month = 1
        next_year += 1
        
    # URLパラメータを作成
    prev_url = f"?year={prev_year}&month={prev_month}"
    next_url = f"?year={next_year}&month={next_month}"
    
    # ----------------------------------------------------
    
    # フィルタリング用のクエリセットを準備
    if user_id is not None:
        all_events = CalendarEvent.objects.filter(user_id=user_id)
    else:
        all_events = CalendarEvent.objects.none()

    # 今日のイベントのみをフィルタリング (表示月に関係なく、常に「今日」の日付を参照)
    today_events = all_events.filter(start_time__date=today).order_by('start_time')
    
    # 月間カレンダーを生成
    cal = CalendarUtil(current_year, current_month) # ★URLから取得した年月を使用
    html_calendar = cal.format_month(all_events)
    
    # 月の名称を取得
    current_month_name = current_date.strftime('%Y年 %m月')


    context = {
        'current_month_name': current_month_name,
        'html_calendar': html_calendar,
        'today_tasks': today_events,
        
        # ★ナビゲーション用のURLを渡す
        'prev_url': prev_url,
        'next_url': next_url,
        
    }

    return render(request, 'auth/top.html', context)

# -----------------------------------------------------------------
# ビュー: イベント追加
# -----------------------------------------------------------------
def add_event(request):
    """ イベント追加フォームの表示とデータ保存を処理 """
    
    user_id = get_current_user_id(request)

    if user_id is None:
        return redirect('top')

    if request.method == 'POST':
        title = request.POST.get('title')
        memo = request.POST.get('memo')
        start_date = request.POST.get('start_date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        color = request.POST.get('color')
        
        # 開始日時が必須であることを確認
        if start_date and start_time_str:
            start_datetime_str = f"{start_date} {start_time_str}"
            try:
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                
                # ★ロジック修正: end_time の決定
                if end_time_str:
                    # 終了時刻がフォームから提供された場合
                    end_datetime_str = f"{start_date} {end_time_str}"
                    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                    
                    # 終了時刻が開始時刻より前の場合、開始時刻に1日加算して日付を修正する（任意）
                    if end_datetime <= start_datetime:
                        end_datetime += timedelta(days=1)
                else:
                    # 終了時刻が省略された場合、開始時刻の1時間後を自動設定
                    end_datetime = start_datetime + timedelta(hours=1)
                
            except ValueError:
                return redirect('top') 
        else:
            return redirect('top') 


        # 重複防止ロジック
        if CalendarEvent.objects.filter(
            user_id=user_id,
            title=title,
            start_time=start_datetime
        ).exists():
            return redirect('top')
        

        # データベースに保存
        CalendarEvent.objects.create(
            user_id=user_id,
            title=title,
            memo=memo,
            start_time=start_datetime,
            end_time=end_datetime, # 決定されたend_datetimeを使用
            color=color,
        )
        
        return redirect('top')
    
    else:
        # GETリクエスト（フォーム表示）
        context = {
            'today_date': date.today().strftime('%Y-%m-%d'),
        }
        return render(request, 'auth/add_event.html', context)
    
# -----------------------------------------------------------------
# ビュー: イベント詳細
# -----------------------------------------------------------------
def event_detail(request, pk):
    """ 特定のイベントの詳細を表示するビュー """
    
    # URLから渡されたプライマリキー (pk) を使ってイベントを取得
    # CalendarEventのプライマリキーは calendar_id 
    event = get_object_or_404(CalendarEvent, calendar_id=pk)
    
    context = {
        'event': event,
    }
    
    return render(request, 'auth/event_detail.html', context)

# -----------------------------------------------------------------
# ビュー: イベント削除
# -----------------------------------------------------------------
def delete_event(request, event_id):
    """
    指定されたIDのCalendarEventを削除するビュー。
    削除後、TOPページにリダイレクトする。
    """
    user_id = get_current_user_id(request)
    
    if user_id is None:
        return redirect('top') 

    if request.method == 'POST':
        try:
            # ユーザーIDも条件に入れて、他人のイベントを削除できないようにする
            event = CalendarEvent.objects.get(calendar_id=event_id, user_id=user_id)

        
        except CalendarEvent.DoesNotExist:
            # 既に削除されている、またはIDが存在しない場合、TOPへリダイレクト
            return redirect('top')
        
        # イベントを削除
        event.delete()
        
        # 削除完了後、TOPページへリダイレクト
        return redirect('top')
    
    # POSTメソッド以外でのアクセスは許可しない
    return redirect('top')

# -----------------------------------------------------------------
# ビュー: イベント編集
# -----------------------------------------------------------------
def edit_event(request, event_id):
    """
    既存のイベントを編集・更新するビュー。
    """
    user_id = get_current_user_id(request)

    if user_id is None:
        return redirect('top')

    # ユーザーのイベントであることを確認し、イベントを取得
    try:
        # 編集するイベントを取得。ユーザーIDでフィルタすることで権限をチェック
        event = CalendarEvent.objects.get(calendar_id=event_id, user_id=user_id)
    except CalendarEvent.DoesNotExist:
        # イベントが存在しない、またはユーザーのイベントではない場合、TOPへリダイレクト
        return redirect('top')


    if request.method == 'POST':
        # ---------------------------
        # POST処理: データ更新
        # ---------------------------
        title = request.POST.get('title')
        memo = request.POST.get('memo')
        start_date = request.POST.get('start_date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        color = request.POST.get('color')

        if start_date and start_time_str:
            start_datetime_str = f"{start_date} {start_time_str}"
            try:
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                
                # 終了時刻の決定ロジック (add_eventと同じ)
                if end_time_str:
                    # 終了時刻がフォームから提供された場合
                    end_datetime_str = f"{start_date} {end_time_str}"
                    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                    
                    # 終了時刻が開始時刻より前の場合、開始時刻に1日加算する（日付またぎを想定）
                    if end_datetime <= start_datetime:
                        end_datetime += timedelta(days=1)
                else:
                    # 終了時刻が省略された場合、開始時刻の1時間後を自動設定
                    end_datetime = start_datetime + timedelta(hours=1)
                
            except ValueError:
                return redirect('top') # 日付・時刻フォーマットエラー時
        else:
            return redirect('top') # 必須フィールドがない場合

        # ---------------------------
        # イベントオブジェクトを更新し、保存
        # ---------------------------
        event.title = title
        event.memo = memo
        event.start_time = start_datetime
        event.end_time = end_datetime
        event.color = color
        
        event.save() # データベースに保存
        
        # 更新後、イベント詳細ページまたはTOPページへリダイレクト
        # イベント詳細ページがあれば 'event_detail' にリダイレクトするのが自然です
        return redirect('top') 
        # return redirect('event_detail', event_id=event.calendar_id) 


    else:
        # ---------------------------
        # GET処理: フォーム表示
        # ---------------------------
        
        # 15分刻みの時刻リストは不要になったため、ここでは渡しません。
        
        # フォームの初期値として使用するコンテキスト
        context = {
            'event': event, # 既存のイベントオブジェクト
            
            # 日付と時刻をフォームの形式に合わせて抽出
            'start_date_val': event.start_time.strftime('%Y-%m-%d'),
            'start_time_val': event.start_time.strftime('%H:%M'),
            'end_time_val': event.end_time.strftime('%H:%M') if event.end_time else None, 
            'current_color': event.color,
        }
        
        return render(request, 'auth/edit_event.html', context)