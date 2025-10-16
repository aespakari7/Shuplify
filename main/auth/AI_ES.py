import os
import json
import base64 
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold,part #partをtypesモジュールから統合
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# .env ファイルから環境変数を読み込む
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.env'))

# ES添削AI用のシステムプロンプト (Markdown使用を指示し、読みやすいフィードバックを要求)
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
    # APIキーの設定チェック
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        error_message = "サーバー設定エラー: GOOGLE_API_KEY が設定されていません。"
        print(f"ERROR: {error_message}")
        if request.method == 'POST':
            return JsonResponse({"error": error_message}, status=500)
        else:
            return render(request, 'auth/AI_ES.html', {'error': error_message})

    genai.configure(api_key=API_KEY)
    
    # セッションから履歴を取得
    chat_history = request.session.get('chat_history_es', [])

    if request.method == 'GET':
        # HTMLファイル名が AI_ES.html に変わったため修正
        return render(request, 'auth/AI_ES.html', {'chat_history': chat_history})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            image_data_base64 = data.get('imageData')
            mime_type = data.get('mimeType')

            if not user_message and not image_data_base64:
                 return HttpResponseBadRequest("メッセージまたは画像が提供されていません。")

            # --- Gemini APIへの入力 (parts) を構築 ---
            parts = []
            
            # 1. 画像データがあれば、Base64をデコードしてPartsに追加
            if image_data_base64 and mime_type:
                # Base64デコード
                image_bytes = base64.b64decode(image_data_base64)
                parts.append(Part.from_bytes(data=image_bytes, mime_type=mime_type))
                
                # 画像がある場合のプロンプトを調整
                if not user_message:
                     user_message = "この添付されたES画像の内容を添削してください。"
                
                # chat_historyには画像データは保存せず、画像が添付された旨をテキストで記録
                chat_history.append({"role": "user", "parts": [f"[画像添付] {user_message}"]})
            else:
                # 画像がない場合は、テキストメッセージのみを履歴に追加
                 chat_history.append({"role": "user", "parts": [user_message]})
            
            # 2. テキストメッセージをPartsに追加
            parts.append(user_message)

            # モデルの初期化
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=SYSTEM_PROMPT_ES
            )
            
            # チャット履歴を渡し、画像とテキストを含むリクエストを送信
            # 今回のメッセージ（parts）を除いた履歴を渡す
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
    else:
        return HttpResponseBadRequest("このエンドポイントはGETまたはPOSTリクエストのみをサポートしています。")
