# C:\main\auth\AIchat.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.shortcuts import render # redirectは不要
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# ... (APIキーやモデルの設定は変更なし)

# @csrf_exempt を再追加します
@csrf_exempt
def aichat(request):
    # APIキーが設定されていない場合のエラーハンドリング
    if not API_KEY:
        error_message = "サーバー設定エラー: APIキーが設定されていません。"
        print(f"ERROR: {error_message}")
        if request.method == 'POST':
            return JsonResponse({"error": error_message}, status=500)
        else:
            return render(request, 'auth/AIchat.html', {'error': error_message})

    genai.configure(api_key=API_KEY)

    # Djangoセッションからチャット履歴を取得
    chat_history = request.session.get('chat_history', [])

    if request.method == 'GET':
        # GETリクエストの場合は、チャット画面をレンダリングするだけ
        return render(request, 'auth/AIchat.html', {'chat_history': chat_history})

    elif request.method == 'POST':
        try:
            # POSTリクエストはJSONでメッセージを受け取る
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return HttpResponseBadRequest("メッセージが提供されていません。")

            # ユーザーメッセージを履歴に追加
            chat_history.append({"role": "user", "parts": [user_message]})

            # Geminiモデルの初期化とメッセージ送信
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(user_message)

            # Geminiの応答を履歴に追加
            chat_history.append({"role": "model", "parts": [response.text]})

            # 更新された履歴をセッションに保存
            request.session['chat_history'] = chat_history
            request.session.modified = True

            # JavaScriptに返すためにJSONでレスポンスを返す
            return JsonResponse({"response": response.text})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("無効なJSON形式です。")
        except Exception as e:
            print(f"Gemini API 呼び出しエラー: {e}")
            return HttpResponseServerError(f"Gemini API 呼び出し中にエラーが発生しました: {e}")
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")