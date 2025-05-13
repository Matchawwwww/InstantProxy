from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
def proxy(path):
    target_url = request.args.get('url')
    if not target_url:
        return "URLパラメータがありません。", 400

    try:
        resp = requests.request(
            method=request.method,
            url=target_url + '/' + path,
            headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            allow_redirects=False,
            stream=True
        )

        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection', 'content-length']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response
    except requests.exceptions.RequestException as e:
        return f"プロキシエラー: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
