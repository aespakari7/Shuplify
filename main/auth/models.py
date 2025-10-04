# main/auth/models.py

from django.db import models

# ----------------------------------------------------
# カレンダーテーブルのモデル (company_idを削除)
# ----------------------------------------------------
class CalendarEvent(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name="ユーザーID")
    # company_id はDBに存在する可能性がありますが、モデル上は無視します
    title = models.CharField(max_length=255, verbose_name="タイトル")
    memo = models.TextField(blank=True, verbose_name="メモ") # ★企業名はこのフィールドを使う
    start_time = models.DateTimeField(verbose_name="開始日時")
    end_time = models.DateTimeField(verbose_name="終了日時", null=True, blank=True)

    class Meta:
        # DBスキーマが変更されていない場合でも、このモデル定義で動作します。
        managed = False
        db_table = 'calendar' 
        verbose_name = "カレンダーイベント"
        verbose_name_plural = "カレンダーイベント"
        ordering = ['start_time']

    def __str__(self):
        return self.title