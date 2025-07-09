from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # ← ここが必要
]


from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    error_message = None  # 初期値はエラーなし
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
       
        if email != "test@example.com" or password != "pass123":
            error_message = "メールアドレスまたはパスワードが間違っています"
        else:
            return redirect('home')  # 成功時はリダイレクト

    return render(request, 'login.html', {'error': error_message})
