import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.shortcuts import render, redirect # redirect をインポート
from django.http import HttpResponseServerError, HttpResponseBadRequest
from django.urls import reverse # URLを逆引きするためにインポート

# .env ファイルから環境変数を読み込む（プロジェクトのルートディレクトリにある前提）
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# 環境変数からAPIキーを取得
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("エラー: GOOGLE_API_KEY が環境変数に設定されていません。")
    print("プロジェクトのルートディレクトリにある .env ファイルを確認してください。")

# Geminiモデルの設定
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# サーバーサイドでのチャット履歴管理
# Djangoのセッションにチャット履歴を保存するように変更
# chat_sessions 辞書は不要になります
# chat_sessions = {} # この行は削除またはコメントアウト

# @csrf_exempt は不要になります（HTMLフォームで {% csrf_token %} を使うため）
def aichat(request):
    # APIキーが設定されていない場合のエラーハンドリング
    if not API_KEY:
        # Render環境であれば、ログに出力し、管理画面でAPIキーを設定するよう促す
        error_message = "サーバー設定エラー: GOOGLE_API_KEY が設定されていません。管理者にご連絡ください。"
        print(f"ERROR: {error_message}") # サーバーログに出力
        return render(request, 'auth/AIchat.html', {'chat_history': [], 'error': error_message})


    genai.configure(api_key=API_KEY)

    # Djangoセッションからチャット履歴を取得、なければ初期化
    # セッションは辞書のように扱える
    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '').strip()

        if not user_message:
            # メッセージが空の場合でも、現在の履歴で再レンダリング
            return render(request, 'auth/AIchat.html', {'chat_history': chat_history})

        try:
            # ユーザーメッセージを履歴に追加
            chat_history.append({"role": "user", "parts": [user_message]})

            # Geminiモデルの初期化とメッセージ送信
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            chat = model.start_chat(history=chat_history) # 最新の履歴を渡す

            response = chat.send_message(user_message)

            # Geminiの応答を履歴に追加
            chat_history.append({"role": "model", "parts": [response.text]})

            # 更新された履歴をセッションに保存
            request.session['chat_history'] = chat_history
            request.session.modified = True # セッションが変更されたことを明示的にマーク

            # POST後にリダイレクト (PRGパターン: Post/Redirect/Get)
            # これにより、ユーザーがページをリロードしても二重送信を防げる
            return redirect(reverse('aichat')) # 'aichat'という名前のURLにリダイレクト

        except Exception as e:
            print(f"Gemini API 呼び出しエラー: {e}")
            # エラーメッセージを履歴に追加して表示
            chat_history.append({"role": "model", "parts": [f"エラーが発生しました: {e}"]})
            request.session['chat_history'] = chat_history
            request.session.modified = True
            # エラーが発生した場合も再レンダリング（リダイレクトではない）
            return render(request, 'auth/AIchat.html', {'chat_history': chat_history, 'error': f"API呼び出し中にエラー: {e}"})

    elif request.method == 'GET':
        # GETリクエストの場合、現在の履歴をテンプレートに渡してレンダリング
        return render(request, 'auth/AIchat.html', {'chat_history': chat_history})
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")