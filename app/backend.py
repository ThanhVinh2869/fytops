from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_code():
    data = request.get_json()
    auth_code = data.get('code')
    
    if not auth_code:
        return jsonify({'error': 'No code provided'}), 400
    
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'https://your-static-site.com/',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Token exchange failed', 'details': response.text}), 400
    
if __name__ == '__main__':
    app.run (debug=True)