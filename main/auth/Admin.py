# C:\Users\shion\OneDrive\ドキュメント\Shuplify\main\auth\Admin.py

from django.contrib import admin

from .models import CalendarEvent, Prompt 

admin.site.register(CalendarEvent)

admin.site.register(Prompt)
