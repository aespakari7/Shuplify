# C:\main\auth\AI_email.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import requests # ⭐ 追加: Supabaseアクセスに必要 ⭐

# .env ファイルから環境変数を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# -----------------------------------------------------------------
# ⭐ 追加: Supabase接続情報 (AI_ES.pyと共通) ⭐
SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTU1MDkxOSwiZXhwIjoyMDYxMTI2OTE5fQ.Mb2UMHZJSYPcXDujxs4q0Dgvh7tXh38EJpPooqydkZs"
SUPABASE_DB_URL = f"{SUPABASE_URL}/rest/v1/prompts"
# -----------------------------------------------------------------


# メール文添削AI用のシステムプロンプト
# ⭐ データベース連携後も、固定定義として残します（コメントアウトしない）が、関数内でDB値に置き換えられます。
SYSTEM_PROMPT_EMAIL = "あなたはビジネスメールのプロフェッショナルです。ユーザーが作成したメール文を添削し、より丁寧で分かりやすい文章になるように改善案を提案してください。回答は**適切に改行**し、箇条書きなども活用してください。"


# ⭐ 追加: システムプロンプト取得関数 (AI_ES.pyと共通) ⭐
def get_prompt_content(prompt_title):
    """
    Supabaseの'prompts'テーブルから指定されたタイトルのプロンプト内容を取得する。
    """
    try:
        response = requests.get(
            f"{SUPABASE_DB_URL}?title=eq.{prompt_title}&select=content", 
            headers={
                "apikey": SUPABASE_API_KEY, 
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
            }
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0 and 'content' in data[0]:
            return data[0]['content']
        
        print(f"警告: タイトル '{prompt_title}' のプロンプトがデータベースに見つかりませんでした。")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"エラー: Supabaseからプロンプト取得中にエラーが発生しました: {e}")
        return None


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
    
    # ⭐ 追加: データベースからシステムプロンプトを取得 ⭐
    db_system_prompt = get_prompt_content('メール添削用')
    
    if not db_system_prompt:
        error_message = "サーバー設定エラー: 'メール添削用' のシステムプロンプトがデータベースに見つかりませんでした。"
        print(f"ERROR: {error_message}")
        if request.method == 'POST':
            return JsonResponse({"error": error_message}, status=500)
        else:
            return render(request, 'auth/AI_email.html', {'error': error_message})

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
                # ⭐ 変更: データベースから取得したプロンプトを使用 ⭐
                system_instruction=db_system_prompt 
                # system_instruction=SYSTEM_PROMPT_EMAIL # ← 固定プロンプトを使用する場合はこちら
            )
            
            # chat = model.start_chat(history=chat_history)
            # chat_historyに最後のメッセージが追加されているため、historyを調整
            chat = model.start_chat(history=chat_history[:-1]) 
            # response = chat.send_message(user_message)
            # historyにメッセージを追加済みなので、send_messageには最後のユーザーメッセージ部分を渡します
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