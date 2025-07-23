# main/auth/models.py

from django.db import models

class CalendarEvent(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name="ユーザーID")
    company_id = models.IntegerField(verbose_name="会社ID")
    title = models.CharField(max_length=255, verbose_name="タイトル")
    memo = models.TextField(blank=True, verbose_name="メモ")
    start_time = models.DateTimeField(verbose_name="開始日時")
    end_time = models.DateTimeField(verbose_name="終了日時", null=True, blank=True)

    class Meta:
        managed = False # 既存DBテーブルを使用するため
        db_table = 'calendar' # 実際のDBテーブル名を指定
        verbose_name = "カレンダーイベント"
        verbose_name_plural = "カレンダーイベント"
        ordering = ['start_time']

    def __str__(self):
        return self.title