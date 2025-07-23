# main/auth/Top.py

from django.shortcuts import render
# from django.contrib.auth.decorators import login_required # ログイン必須にするため、この行をコメントアウトまたは削除
from datetime import date
from .models import CalendarEvent

# @login_required # この行をコメントアウトまたは削除
def top(request):
    """
    ユーザーのTOPページを表示し、今日のタスクをデータベースから取得して渡すビュー
    """
    # ユーザーがログインしていない場合、request.user.id は通常 anonymous user のID となるか、エラーになる可能性があります。
    # セッションなしで進める場合、ここでは仮のユーザーIDを使用するか、
    # ログイン機能が実装されるまで CalendarEvent のフィルタリングを一時的に変更する必要があります。
    # 例: デバッグ用に特定のユーザーIDを使用
    # user_id = 1 # 仮のユーザーID (開発用)
    # または、ユーザーIDなしで全てのイベントを取得
    # today_events = CalendarEvent.objects.filter(start_time__date=today).order_by('start_time')

    # 現在はログインをスキップするため、仮のユーザーIDを使用するか、この部分を一時的に無効にするのが良いでしょう。
    # ここでは、ログイン後にrequest.user.idが設定されることを前提としているため、
    # ログインなしでアクセスするとエラーになる可能性があります。
    # 開発中は、一旦このフィルタリングをなくすか、ダミーのデータを使用することを検討してください。
    user_id = request.user.id # ログインが有効になるまでは、この行は注意が必要です。

    today = date.today()

    # 現在のユーザーに紐づく今日のカレンダーイベントを取得
    today_events = CalendarEvent.objects.filter(
        user_id=user_id, # user_id が存在しない場合、エラーになる可能性があります
        start_time__date=today
    ).order_by('start_time')

    # テンプレートに渡すコンテキストデータ
    context = {
        'today_tasks': today_events,
        'profile_url': '/profile/', # 仮のURL、実際のURLパスに合わせて修正してください
        'chat_url': '/AIchat/',
        'self_analysis_url': '/self-analysis/',
        'calendar_detail_url': '/calendar-detail/',
        'es_edit_url': '/es-edit/',
        'company_analysis_url': '/company-analysis/',
        'mail_edit_url': '/mail-edit/',
        'company_manage_url': '/company-manage/',
    }

    # 'main/auth/templates/auth/top.html' をレンダリング
    return render(request, 'auth/top.html', context)