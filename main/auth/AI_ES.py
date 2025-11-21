import os
import json
import base64 
import google.generativeai as genai
# types を Blob のためにインポートします
from google.generativeai import types, upload_file 
from google.generativeai.types import HarmCategory, HarmBlockThreshold 
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
# import tempfile # 修正: 不要になるため削除
import requests #☆追加
import tempfile #☆追加
import uuid #☆追加

# .env ファイルから環境変数を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# -----------------------------------------------------------------
# Supabase接続情報
# -----------------------------------------------------------------
SUPABASE_URL = "https://uzoblakkftugdweloxku.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6b2JsYWtrZnR1Z2R3ZWxveGt1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTU1MDkxOSwiZXhwIjoyMDYxMTI2OTE5fQ.Mb2UMHZJSYPcXDujxs4q0Dgvh7tXh38EJpPooqydkZs"
SUPABASE_DB_URL = f"{SUPABASE_URL}/rest/v1/prompts"

#☆システムプロンプト取得関数
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
    
# 設定 (変更なし)
generation_config = {
    "temperature": 0.5, 
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
def aies(request):
    # APIキーの設定チェック (変更なし)
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        error_message = "サーバー設定エラー: GOOGLE_API_KEY が設定されていません。"
        print(f"ERROR: {error_message}")
        if request.method == 'POST':
            return JsonResponse({"error": error_message}, status=500)
        else:
            return render(request, 'auth/AI_ES.html', {'error': error_message})

    genai.configure(api_key=API_KEY)
    
    #☆データベースからシステムプロンプトを取得
    db_system_prompt = get_prompt_content('ES添削用')
    
    if not db_system_prompt:
        error_message = "サーバー設定エラー: 'ES添削用' のシステムプロンプトがデータベースに見つかりませんでした。"
        print(f"ERROR: {error_message}")
        if request.method == 'POST':
            return JsonResponse({"error": error_message}, status=500)
        else:
            return render(request, 'auth/AI_ES.html', {'error': error_message})
        
    chat_history = request.session.get('chat_history_es', [])

    if request.method == 'GET':
        return render(request, 'auth/AI_ES.html', {'chat_history': chat_history})

    # ▼▼▼ 修正: POST処理全体を修正  ▼▼▼
    elif request.method == 'POST':
       
        uploaded_file = None  #クリーンアップのためにファイル参照を保持
        temp_file_path = None 

        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            file_data_base64 = data.get('imageData') 
            mime_type = data.get('mimeType')

            if not user_message and not file_data_base64:
                return HttpResponseBadRequest("メッセージまたはファイルが提供されていません。")

            parts = []
            
            # --- ファイル処理 (Blob を使用) ---
            if file_data_base64 and mime_type:
                
                #　★追加：　PDF以外ファイルを拒否
                if mime_type != 'application/pdf':
                    return HttpResponseBadRequest("サポートされていないファイル形式です。PDFファイルのみをアップロードしてください。")
                try:
                    # Base64をデコードしてバイトデータを取得
                    file_bytes = base64.b64decode(file_data_base64)
                except (base64.binascii.Error, ValueError) as e:
                    return HttpResponseBadRequest(f"無効なBase64データ形式です: {e}")
                #Base64データから一時のファイルを作成
                ext = '.pdf' if mime_type == 'application/pdf' else '.dat'
                temp_filepath = os.path.join(tempfile.gettempdir(),str(uuid.uuid4()) + ext)
                with open(temp_filepath, 'wb') as f:
                    f.write(file_bytes)

                #一時ファイルをGemini　API　のサービスにアップロード
                print(f"DEBUG: uploading file: {temp_filepath}...")
                # upload_file はファイルを読み取り、Gemini_file_APIのエンドポイントにアップロードし、Fileオブジェクトを返す
                uploaded_file = genai.upload_file(file=temp_filepath)
                print(f"DEBUG: upload success, file name: {uploaded_file.name}")

                parts.append(uploaded_file)
                
                # 修正: tempfile, upload_file, os.unlink の処理はすべて不要

                if not user_message:
                    user_message = f"この添付ファイル（{mime_type}）の内容を添削してください。"

                #チャット履歴には添付ファイル情報とユーザーメッセージの記録
                chat_history.append({"role": "user", "parts": [f"[ファイル添付: {mime_type}] {user_message}"]})
            
            else:
                # テキストのみの場合
                chat_history.append({"role": "user", "parts": [user_message]})
            
            # テキストメッセージをPartsに追加
            parts.append(user_message)

            # --- モデルの初期化とAPI呼び出し ---
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=generation_config,
                safety_settings=safety_settings,
                #☆変更
                system_instruction=db_system_prompt
            )
            #過去のチャット履歴を使用してチャットを開始
            chat = model.start_chat(history=chat_history[:-1])

            #新しいメッセージ(テキストとアップロードファイル)を送信
            response = chat.send_message(parts)
            
            #レスポンスを履歴に追加
            chat_history.append({"role": "model", "parts": [response.text]})
            request.session['chat_history_es'] = chat_history
            request.session.modified = True

            return JsonResponse({"response": response.text})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("無効なJSON形式です。")
        except Exception as e:
            error_message = f"Gemini API 呼び出し中にエラーが発生しました: {e}"
            print(error_message) # サーバーログには詳細なエラーを残す
            # ユーザーには 'ragStoreName' のような内部エラーは見せない
            return JsonResponse({"error": "AIモデルの呼び出し中にエラーが発生しました。"}, status=500)
        
        finally:
            #　★重要：　アップロードした一時ファイルとGemini上のファイルをクリーンアップ

            #1.Gemini_File_API上のファイルを削除
            if uploaded_file:
                try:
                    print(f"DEBUG: deleting uploaded file: {uploaded_file.name}")
                    genai.delete_file(name=uploaded_file.name)
                except Exception as e:
                    print(f"WARNING: Failed to delete Gemini file {uploaded_file.name}: {e}")

            #2.サーバー上の一時ファイルを削除
            if temp_filepath and os.path.exists(temp_filepath):
                try:
                    os.unlink(temp_filepath)
                    print(f"DEBUG: local_temp_file deleted: {temp_filepath}")
                except Exception as e:
                    print(f"WARNING: Failed to delete local temp file {temp_filepath}: {e}")

            pass
    # ▲▲▲ 修正 ▲▲▲
            
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")