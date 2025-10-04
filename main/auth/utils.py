# main/auth/utils.py
import calendar
from datetime import date, timedelta

class CalendarUtil:
    """
    月間カレンダーのHTMLを生成するユーティリティクラス。
    デザイン用のクラス名のみを付与し、スタイルはHTML側で定義する。
    """
    def __init__(self, year, month):
        self.year = year
        self.month = month
        # 週の始まりを日曜（6）に設定
        self.cal = calendar.Calendar(firstweekday=6)

    def format_day(self, day, events):
        """ カレンダーの特定の日 (day) のセルHTMLを生成する """
        
        # 該当日のイベントを取得
        if day != 0:
            events_on_day = events.filter(start_time__date=date(self.year, self.month, day))
        else:
            events_on_day = []

        # 今日の日付かチェック
        is_today = (day == date.today().day and self.month == date.today().month and self.year == date.today().year)

        html = []
        
        if day == 0:
            # 0は前月または翌月の日付
            html.append('<td class="cal-noday"></td>')
            return ''.join(html)
        
        # セルのクラスを設定
        day_class = "cal-day"
        if is_today:
            day_class += " cal-today"

        html.append(f'<td class="{day_class}">')
        html.append(f'<span class="cal-date">{day}</span>') # 日付番号
        
        # イベントリストのコンテナ
        html.append('<div class="cal-events-list">')
        for event in events_on_day:
            # イベントをリンクとして表示し、デザインクラスを付与
            html.append(f'<a href="/main/auth/calendar-detail/{event.id}/" class="cal-event-item">')
            html.append(f'<span>{event.title}</span>')
            html.append('</a>')
        html.append('</div>')
        
        html.append('</td>')
        return ''.join(html)

    def format_week(self, week, events):
        """ 週のHTML（<tr>）を生成する """
        week_html = []
        for d, _ in week:
            week_html.append(self.format_day(d, events))
        return f'<tr class="cal-week-row">{"".join(week_html)}</tr>'

    def format_month(self, events):
        """ 月間カレンダー全体のHTMLを生成する """
        
        # テーブルのヘッダー（日、月、火...）
        month_names = ['日', '月', '火', '水', '木', '金', '土']
        cal_header = ''.join(f'<th class="cal-header-day">{name}</th>' for name in month_names)
        
        html = [
            '<table class="cal-table">',
            f'<thead><tr class="cal-header-row">{cal_header}</tr></thead>',
            '<tbody>'
        ]

        # monthdays2calendarは、(日付, 曜日)のタプルのリストを返す
        for week in self.cal.monthdays2calendar(self.year, self.month):
            html.append(self.format_week(week, events))

        html.append('</tbody>')
        html.append('</table>')
        return ''.join(html)