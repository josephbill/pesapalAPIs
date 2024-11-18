from flask import Flask, request, jsonify
import requests
from utils.constants import consumer_key,consumer_secret,base_url


app = Flask(__name__)
# CORS(app)

@app.route('/get-pesapal-token', methods=['POST'])
def get_pesapaltoken():
    # pesapal token URL 
    token_url= f"{base_url}/api/Auth/RequestToken"
    print(token_url)
    # consumer key and secret object
    authtokens = {
        "consumer_key" : "a0VglCdF8eS2+DmtRALSUmBHQ4m/dkj5",
        "consumer_secret" : "xY1Yl9FC/YKROa+VYwB5DxhT/Bg="
    }
    
    print(authtokens)
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept" : "application/json"
        }
        
        response = requests.post(token_url, json=authtokens, headers=headers)
        # check success response 
        response.raise_for_status()
        
        #return 
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500
    
    
    

if __name__ == '__main__':
    app.run(port=5000)
        
    