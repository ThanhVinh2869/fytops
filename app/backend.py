from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_code():
    data = request.get_json()
    auth_code = data.get('code')
    
    if not auth_code:
        return jsonify({'error': 'No code provided'}), 400

    print(auth_code)
    
if __name__ == '__main__':
    app.run (debug=True)