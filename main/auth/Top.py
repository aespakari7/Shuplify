# main/auth/Top.py

from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, datetime, timedelta
from .models import CalendarEvent
from .utils import CalendarUtil
# from .models import CalendarEvent, UserProfile
# from django.contrib.auth.models import User


# -----------------------------------------------------------------
# ヘルパー関数: ユーザーIDの取得（Supabase UUID対応版）
# -----------------------------------------------------------------
def get_current_user_id(request):
    """
    Supabase セッションから 'uuid' 型の user_id を取得する。
    """
    supa = request.session.get("user")
    
    if supa:
        # Supabaseセッションには、Authが発行したユーザーのUUIDが含まれているはず
        # Supabase AuthのJWTデコード後のJSON構造に依存
        user_uuid = supa.get("id") # サインアップ処理でAuthから取得したキー
        
        # ログイン処理を実装していないため、セッションに 'id' がない場合は
        # 'user'オブジェクトから取得を試みる (サインアップ時のレスポンス構造)
        if not user_uuid and supa.get("user"):
            user_uuid = supa["user"].get("id")

        if user_uuid:
            # 取得した UUID（文字列）を返す
            return user_uuid

    # ログインしていない場合（UUIDを取得できない場合は None を返す）
    return None


# -----------------------------------------------------------------
# ビュー: TOPページ（カレンダー表示）
# -----------------------------------------------------------------
def top(request):

    user_id = get_current_user_id(request)

    today = date.today()

    current_year = today.year
    current_month = today.month

    year_str = request.GET.get('year')
    month_str = request.GET.get('month')

    try:
        if year_str and month_str:
            current_year = int(year_str)
            current_month = int(month_str)
    except ValueError:
        pass

    current_date = date(current_year, current_month, 1)

    prev_month = current_month - 1
    prev_year = current_year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = current_month + 1
    next_year = current_year
    if next_month == 13:
        next_month = 1
        next_year += 1

    prev_url = f"?year={prev_year}&month={prev_month}"
    next_url = f"?year={next_year}&month={next_month}"

    # ユーザーのイベント取得
    if user_id:
        all_events = CalendarEvent.objects.filter(user_id=user_id)
    else:
        all_events = CalendarEvent.objects.none()

    today_events = all_events.filter(start_time__date=today).order_by('start_time')

    cal = CalendarUtil(current_year, current_month)
    html_calendar = cal.format_month(all_events)

    current_month_name = current_date.strftime('%Y年 %m月')

    context = {
        'current_month_name': current_month_name,
        'html_calendar': html_calendar,
        'today_tasks': today_events,
        'prev_url': prev_url,
        'next_url': next_url,
    }

    return render(request, 'auth/top.html', context)


# -----------------------------------------------------------------
# イベント追加
# -----------------------------------------------------------------
def add_event(request):

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

        if start_date and start_time_str:
            start_datetime_str = f"{start_date} {start_time_str}"
            try:
                start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')

                if end_time_str:
                    end_datetime_str = f"{start_date} {end_time_str}"
                    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')

                    if end_datetime <= start_datetime:
                        end_datetime += timedelta(days=1)
                else:
                    end_datetime = start_datetime + timedelta(hours=1)

            except ValueError:
                return redirect('top')
        else:
            return redirect('top')

        if CalendarEvent.objects.filter(
            user_id=user_id,
            title=title,
            start_time=start_datetime
        ).exists():
            return redirect('top')

        CalendarEvent.objects.create(
            user_id=user_id,
            title=title,
            memo=memo,
            start_time=start_datetime,
            end_time=end_datetime,
            color=color,
        )

        return redirect('top')

    context = {
        'today_date': date.today().strftime('%Y-%m-%d'),
    }

    return render(request, 'auth/add_event.html', context)


# -----------------------------------------------------------------
# イベント詳細
# -----------------------------------------------------------------
def event_detail(request, pk):
    event = get_object_or_404(CalendarEvent, calendar_id=pk)
    return render(request, 'auth/event_detail.html', {'event': event})


# -----------------------------------------------------------------
# イベント削除
# -----------------------------------------------------------------
def delete_event(request, event_id):

    user_id = get_current_user_id(request)
    if user_id is None:
        return redirect('top')

    if request.method == 'POST':
        try:
            event = CalendarEvent.objects.get(calendar_id=event_id, user_id=user_id)
        except CalendarEvent.DoesNotExist:
            return redirect('top')

        event.delete()
        return redirect('top')

    return redirect('top')


# -----------------------------------------------------------------
# イベント編集
# -----------------------------------------------------------------
def edit_event(request, event_id):

    user_id = get_current_user_id(request)
    if user_id is None:
        return redirect('top')

    try:
        event = CalendarEvent.objects.get(calendar_id=event_id, user_id=user_id)
    except CalendarEvent.DoesNotExist:
        return redirect('top')

    if request.method == 'POST':
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

                if end_time_str:
                    end_datetime_str = f"{start_date} {end_time_str}"
                    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')

                    if end_datetime <= start_datetime:
                        end_datetime += timedelta(days=1)
                else:
                    end_datetime = start_datetime + timedelta(hours=1)

            except ValueError:
                return redirect('top')
        else:
            return redirect('top')

        event.title = title
        event.memo = memo
        event.start_time = start_datetime
        event.end_time = end_datetime
        event.color = color
        event.save()

        return redirect('top')

    context = {
        'event': event,
        'start_date_val': event.start_time.strftime('%Y-%m-%d'),
        'start_time_val': event.start_time.strftime('%H:%M'),
        'end_time_val': event.end_time.strftime('%H:%M') if event.end_time else None,
        'current_color': event.color,
    }

    return render(request, 'auth/edit_event.html', context)
