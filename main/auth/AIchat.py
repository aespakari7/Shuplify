# C:\main\auth\AIchat.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# .env ファイルから環境変数を読み込む（プロジェクトのルートディレクトリにある前提）
# Djangoプロジェクトの場合、settings.py で設定することも多いですが、
# ここではビュー関数内で読み込みます。
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# 環境変数からAPIキーを取得
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    # 開発中にAPIキーが設定されていない場合のエラーハンドリング
    # 本番環境では、より堅牢な方法でエラーをログに記録し、ユーザーには抽象的なエラーメッセージを表示します
    print("エラー: GOOGLE_API_KEY が環境変数に設定されていません。")
    print("プロジェクトのルートディレクトリにある .env ファイルを確認してください。")
    # デバッグのために、エラーメッセージをHTTPレスポンスにも含める
    # しかし、本番環境ではAPIキーに関する情報を外部に漏らさないよう注意が必要です。

# Geminiモデルの設定
# safety_settings は必要に応じて調整してください
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

# セッションごとにチャット履歴を保持するための辞書
# 実際の本番環境では、データベースやDjangoのセッションフレームワークを使用して
# ユーザーごとの永続的な履歴を管理する必要があります。
# これは開発・テスト用の簡易的な実装です。
chat_sessions = {}

@csrf_exempt # CSRFトークンを一時的に無効にします。本番環境では適切にCSRFトークンを扱う必要があります。
def aichat(request):
    if request.method == 'GET':
        # AIchat.html テンプレートをレンダリングして返す
        return render(request, 'auth/AIchat.html')

    elif request.method == 'POST':
        if not API_KEY:
            return JsonResponse({"error": "サーバー設定エラー: APIキーが設定されていません。"}, status=500)

        genai.configure(api_key=API_KEY)

        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            session_id = request.session.session_key # DjangoのセッションIDを取得

            if not user_message:
                return HttpResponseBadRequest("メッセージが提供されていません。")

            if not session_id:
                request.session.save() # セッションがまだ存在しない場合は保存してIDを生成
                session_id = request.session.session_key

            # セッションIDに基づいてチャット履歴を取得または初期化
            if session_id not in chat_sessions:
                chat_sessions[session_id] = []

            history = chat_sessions[session_id]

            # モデルを初期化（履歴はセッションごとに管理）
            # history は chat.send_message() を呼び出すたびに更新される
            model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            chat = model.start_chat(history=history)

            # ユーザーメッセージを送信
            response = chat.send_message(user_message)

            # チャット履歴を更新
            # Gemini APIのhistoryは、ユーザーとモデルのペアで保存されます
            history.append({"role": "user", "parts": [user_message]})
            history.append({"role": "model", "parts": [response.text]})

            return JsonResponse({"response": response.text})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("無効なJSON形式です。")
        except Exception as e:
            print(f"Gemini API 呼び出しエラー: {e}")
            return HttpResponseServerError(f"Gemini API 呼び出し中にエラーが発生しました: {e}")
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")