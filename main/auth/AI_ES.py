import os
import json
import base64
import uuid
import tempfile
import requests

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# -------------------------------------------------
# 環境変数ロード
# -------------------------------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# -------------------------------------------------
# Supabase 設定
# -------------------------------------------------
SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")  # ★ env推奨
SUPABASE_DB_URL = f"{SUPABASE_URL}/rest/v1/prompts"

# -------------------------------------------------
# Supabase からシステムプロンプト取得
# -------------------------------------------------
def get_prompt_content(title: str) -> str | None:
    try:
        res = requests.get(
            f"{SUPABASE_DB_URL}?title=eq.{title}&select=content",
            headers={
                "apikey": SUPABASE_API_KEY,
                "Authorization": f"Bearer {SUPABASE_API_KEY}",
            },
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
        return data[0]["content"] if data else None
    except Exception as e:
        print(f"[Supabase ERROR] {e}")
        return None

# -------------------------------------------------
# Gemini 設定
# -------------------------------------------------
GENERATION_CONFIG = {
    "temperature": 0.5,
    "top_p": 1.0,
    "top_k": 1,
    "max_output_tokens": 2048,
}

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# -------------------------------------------------
# View
# -------------------------------------------------
@csrf_exempt
def aies(request):

    # API Key チェック
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        return JsonResponse({"error": "GOOGLE_API_KEY が未設定です"}, status=500)

    genai.configure(api_key=API_KEY)

    system_prompt = get_prompt_content("ES添削用")
    if not system_prompt:
        return JsonResponse({"error": "システムプロンプトが取得できません"}, status=500)

    chat_history = request.session.get("chat_history_es", [])

    if request.method == "GET":
        return render(request, "auth/AI_ES.html", {"chat_history": chat_history})

    if request.method != "POST":
        return HttpResponseBadRequest("GET / POST のみ対応")

    uploaded_file = None
    temp_filepath = None

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()
        file_base64 = body.get("imageData")
        mime_type = body.get("mimeType")

        if not user_message and not file_base64:
            return HttpResponseBadRequest("入力がありません")

        parts = []

        # ------------------------
        # PDF 処理
        # ------------------------
        if file_base64:
            if mime_type != "application/pdf":
                return HttpResponseBadRequest("PDFのみ対応しています")

            file_bytes = base64.b64decode(file_base64)
            temp_filepath = os.path.join(
                tempfile.gettempdir(),
                f"{uuid.uuid4()}.pdf"
            )

            with open(temp_filepath, "wb") as f:
                f.write(file_bytes)

            print(f"[DEBUG] Uploading: {temp_filepath}")
            uploaded_file = genai.upload_file(temp_filepath)
            print(f"[DEBUG] Uploaded Gemini file: {uploaded_file.name}")

            parts.append(uploaded_file)

            if not user_message:
                user_message = "このPDFを添削してください。"

            chat_history.append({
                "role": "user",
                "parts": [f"[PDF添付] {user_message}"]
            })

        else:
            chat_history.append({
                "role": "user",
                "parts": [user_message]
            })

        parts.append(user_message)

        # ------------------------
        # Gemini 呼び出し
        # ------------------------
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
            system_instruction=system_prompt,
        )

        chat = model.start_chat(history=chat_history[:-1])
        response = chat.send_message(parts)

        chat_history.append({
            "role": "model",
            "parts": [response.text]
        })

        request.session["chat_history_es"] = chat_history

        return JsonResponse({"response": response.text})

    except Exception as e:
        print(f"[Gemini ERROR] {e}")
        return JsonResponse(
            {"error": "AI処理中にエラーが発生しました"},
            status=500
        )

    finally:
        # Geminiファイル削除
        if uploaded_file:
            try:
                genai.delete_file(uploaded_file.name)
                print(f"[DEBUG] Gemini file deleted: {uploaded_file.name}")
            except Exception as e:
                print(f"[WARN] Gemini file delete failed: {e}")

        # ローカル一時ファイル削除
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.unlink(temp_filepath)
                print(f"[DEBUG] Local temp deleted: {temp_filepath}")
            except Exception as e:
                print(f"[WARN] Temp file delete failed: {e}")
