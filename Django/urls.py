# プロジェクトのルート urls.py

from django.urls import path, include

urlpatterns = [

    path('main/auth/', include('main.auth.urls')),
    path('admin/', include('Admin.urls')), 
]