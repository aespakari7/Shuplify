# C:\main\auth\AI_email.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# .env ファイルから環境変数を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# メール文添削AI用のシステムプロンプト
SYSTEM_PROMPT_EMAIL = "あなたはビジネスメールのプロフェッショナルです。ユーザーが作成したメール文を添削し、より丁寧で分かりやすい文章になるように改善案を提案してください。回答はHTMLの<br>タグを使って**適切に改行**し、箇条書きなども活用してください。"

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

@csrf_exempt
def aiemail(request):
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        error_message = "サーバー設定エラー: GOOGLE_API_KEY が設定されていません。"
        print(f"ERROR: {error_message}")
        if request.method == 'POST':
            return JsonResponse({"error": error_message}, status=500)
        else:
            return render(request, 'auth/AI_email.html', {'error': error_message})

    genai.configure(api_key=API_KEY)
    chat_history = request.session.get('chat_history_email', [])

    if request.method == 'GET':
        return render(request, 'auth/AI_email.html', {'chat_history': chat_history})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            if not user_message:
                return HttpResponseBadRequest("メッセージが提供されていません。")

            chat_history.append({"role": "user", "parts": [user_message]})

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=SYSTEM_PROMPT_EMAIL
            )
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(user_message)
            chat_history.append({"role": "model", "parts": [response.text]})

            request.session['chat_history_email'] = chat_history
            request.session.modified = True

            return JsonResponse({"response": response.text})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("無効なJSON形式です。")
        except Exception as e:
            print(f"Gemini API 呼び出しエラー: {e}")
            return HttpResponseServerError(f"Gemini API 呼び出し中にエラーが発生しました: {e}")
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")