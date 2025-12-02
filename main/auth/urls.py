# main/auth/urls.py

from django.urls import path
from . import Sign_up
from . import Login
from . import Top
from . import AI_ES
from . import AI_email
from django.views.generic import TemplateView

urlpatterns = [
    path('signup/', Sign_up.signup, name='signup'), # /main/auth/signup/ で実行される
    path('login/', Login.login, name='login'), # /main/auth/login/ で実行される
    path('top/', Top.top, name='top'), # /main/auth/top/ で実行される
    path('confirm-email/', TemplateView.as_view(template_name='auth/confirm_email.html'), name='confirm_email'),
    path('es-tutor/', AI_ES.aies, name='es_tutor'), # /main/auth/es-tutor/ で実行される
    path('email-tutor/', AI_email.aiemail, name='email_tutor'),# /main/auth/email-tutor/ で実行される
    path('add-event/', Top.add_event, name='add_event'), # /main/auth/add-event/ で実行される
    path('calendar-detail/<int:pk>/', Top.event_detail, name='calendar_detail'), # /main/auth/calendar-detail/ で実行される
    path('delete-event/<int:event_id>/', Top.delete_event, name='delete_event'),# /main/auth/delete-event/ で実行される
    path('edit-event/<int:event_id>/', Top.edit_event, name='edit_event'), # /main/auth/edit-event/ で実行される
    path('auth/process_token/', Top.process_supabase_token, name='process_token'),
]