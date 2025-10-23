# main/auth/models.py

from django.db import models

# ----------------------------------------------------
# カレンダーテーブルのモデル
# ----------------------------------------------------
class CalendarEvent(models.Model):
    calendar_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name="ユーザーID")
    title = models.CharField(max_length=255, verbose_name="タイトル")
    memo = models.TextField(blank=True, verbose_name="メモ")
    start_time = models.DateTimeField(verbose_name="開始日時")
    end_time = models.DateTimeField(verbose_name="終了日時", null=True, blank=True)
    COLOR_CHOICES = [
        ('blue', '面接 (青)'),
        ('green', '説明会 (緑)'),
        ('red', '自己分析 (赤)'),
        ('yellow', 'その他 (黄)'),
    ]
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='blue')

    class Meta:
        # DBスキーマが変更されていない場合でも、このモデル定義で動作します。
        managed = False
        db_table = 'calendar' 
        verbose_name = "カレンダーイベント"
        verbose_name_plural = "カレンダーイベント"
        ordering = ['start_time']

    def __str__(self):
        return self.title

# ----------------------------------------------------
# プロンプト管理テーブルのモデル
# ----------------------------------------------------
class Prompt(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="プロンプト名")
    content = models.TextField(verbose_name="プロンプト内容")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最終更新日時")

    class Meta:
        # DBに実際にPromptテーブルを作成する場合は、managed=True (または記述しない) にします
        # 既存のテーブルをマッピングする場合は managed=False にします
        # 今回は新規作成なので、managed=Falseは削除またはmanaged=Trueとします
        # managed = True # またはこの行を削除
        verbose_name = "プロンプト"
        verbose_name_plural = "プロンプト"

    def __str__(self):
        return self.name
