from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>ようこそ Shuplify へ！</h1><p>これは Azure にデプロイされたアプリです。</p>"
