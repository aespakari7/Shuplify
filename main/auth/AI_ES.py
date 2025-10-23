import os
import json
import base64 
import google.generativeai as genai
from google.generativeai import types, upload_file
from google.generativeai.types import HarmCategory, HarmBlockThreshold 
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import tempfile # tempfile をインポート

# .env ファイルから環境変数を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# システムプロンプト (変更なし)
SYSTEM_PROMPT_ES = """
あなたは就活専門のキャリアアドバイザーです。
ES（エントリーシート）の内容（入力テキストおよび添付画像）を添削し、より魅力的になるように具体的にアドバイスしてください。

【出力形式の原則】
1. **Markdownを使用**し、見出し、箇条書き、太字を活用して、添削結果を視覚的に分かりやすく構成してください。
2. 添削内容は以下の3つの主要なセクションで構成してください。
    - **【評価と総評】**: ESの強みと改善点を簡潔に総括する。
    - **【具体的な改善案】**: 具体的な言葉遣い、エピソードの構成、企業への貢献度に焦点を当てたアドバイスを箇条書きで提供する。
    - **【次のステップ】**: 添削後の質問や検討事項を提示し、より良いESを作成するための指針を与える。
3. 表現の多様性を保つため、同じ言葉（漢字、ひらがな、カタカナを問わず）を二回連続で使用することは避けてください。
"""

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
    
    # セッションから履歴を取得 (変更なし)
    chat_history = request.session.get('chat_history_es', [])

    if request.method == 'GET':
        return render(request, 'auth/AI_ES.html', {'chat_history': chat_history})

    # ▼▼▼ 修正点: POST処理全体を修正 ▼▼▼
    elif request.method == 'POST':
        uploaded_file = None # Google File API オブジェクト
        temp_filepath = None # サーバー上の一時ファイルパス

        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            # (推奨) 変数名を imageData -> file_data_base64 に変更
            file_data_base64 = data.get('imageData') 
            mime_type = data.get('mimeType')

            if not user_message and not file_data_base64:
                return HttpResponseBadRequest("メッセージまたは画像が提供されていません。")

            parts = []
            
            # --- ファイル処理 ---
            if file_data_base64 and mime_type:
                
                try:
                    # (修正点 3) Base64デコードとエラーハンドリング
                    file_bytes = base64.b64decode(file_data_base64)
                except (base64.binascii.Error, ValueError) as e:
                    return HttpResponseBadRequest(f"無効なBase64データ形式です: {e}")

                # 拡張子を決定 (デバッグ用、無くても良い)
                extension_map = {
                    'application/pdf': 'pdf',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                    'application/msword': 'doc',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
                    'application/vnd.ms-excel': 'xls',
                    'text/plain': 'txt'
                }
                if mime_type.startswith('image/'):
                    suffix = f".{mime_type.split('/')[-1].split('+')[0]}" #例: image/svg+xml
                else:
                    suffix = f".{extension_map.get(mime_type, 'bin')}"

                # テンポラリファイルを作成し、バイトデータを書き込む
                with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix=suffix) as tmp:
                    tmp.write(file_bytes)
                    temp_filepath = tmp.name # パスを記憶

                # (修正点 1) ファイルをGeminiにアップロード (引数を 'path' に修正)
                uploaded_file = genai.upload_file(path=temp_filepath, mime_type=mime_type)
                parts.append(uploaded_file)
                
                # (修正点 2) アップロード後、テンポラリファイルを即座に削除
                os.unlink(temp_filepath)
                temp_filepath = None # 削除したので None に戻す

                # メッセージがない場合は、ファイルタイプを補足
                if not user_message:
                    user_message = f"この添付ファイル（{mime_type}）の内容を添削してください。"
                
                chat_history.append({"role": "user", "parts": [f"[ファイル添付: {mime_type}] {user_message}"]})
            
            else:
                # テキストのみの場合
                chat_history.append({"role": "user", "parts": [user_message]})
            
            # テキストメッセージをPartsに追加
            parts.append(user_message)

            # --- モデルの初期化とAPI呼び出し ---
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", # (推奨) 1.5-flash または 1.5-pro がファイル処理に強い
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=SYSTEM_PROMPT_ES
            )
            
            chat = model.start_chat(history=chat_history[:-1]) 
            response = chat.send_message(parts)
            
            # 応答を履歴に追加
            chat_history.append({"role": "model", "parts": [response.text]})

            # セッションを更新
            request.session['chat_history_es'] = chat_history
            request.session.modified = True

            return JsonResponse({"response": response.text})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("無効なJSON形式です。")
        except Exception as e:
            error_message = f"Gemini API 呼び出し中にエラーが発生しました: {e}"
            print(error_message)
            return JsonResponse({"error": error_message}, status=500)
        
        finally:
            # (修正点 2) 途中でエラーが発生した場合に備え、テンポラリファイルが残っていれば削除
            if temp_filepath and os.path.exists(temp_filepath):
                print(f"クリーンアップ: 残存した一時ファイル {temp_filepath} を削除します。")
                os.unlink(temp_filepath)
                
            # (修正点 2) Google側にアップロードしたファイルを削除（非常に重要）
            if uploaded_file:
                try:
                    genai.delete_file(name=uploaded_file.name)
                except Exception as e:
                    # ここでのエラーはログに残すが、クライアントには影響させない
                    print(f"警告: Google File APIからのファイル削除に失敗しました (Name: {uploaded_file.name}): {e}")
    # ▲▲▲ 修正点 ▲▲▲
            
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")