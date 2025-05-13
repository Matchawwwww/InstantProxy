from flask import Flask, request, Response, render_template
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/proxy', methods=['GET'])
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URLパラメータがありません。", 400

    try:
        parsed_url = urlparse(target_url)
        if not parsed_url.scheme:
            target_url = "http://" + target_url  # スキームがない場合はhttpをデフォルトとする

        resp = requests.get(
            target_url,
            headers={key: value for (key, value) in request.headers if key.lower() not in ['host', 'x-forwarded-for']},
            stream=True,
            allow_redirects=False  # リダイレクトはクライアントに処理させる
        )

        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection', 'content-length']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except requests.exceptions.RequestException as e:
        return f"プロキシエラー: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
