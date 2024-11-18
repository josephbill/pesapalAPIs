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
        "consumer_key" : consumer_key,
        "consumer_secret" : consumer_secret
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
    
@app.route('/registerIPNURL', methods=['POST'])
def register_ipn():
    ipn_url = f"{base_url}/api/URLSetup/RegisterIPN"
    
    data = request.get_json()
    session_token = data.get("sessionToken")
    # redirect URL : callback URL that pesapal sends the notifications to
    redirect_url = "https://friendly-nougat-e4e413.netlify.app/" # simple hosted .html page that pesapal can link to 
    
    # prep IPN request payload 
    ipn_request_payload = {
        "url" : redirect_url,
        "ipn_notification_type": "GET"
    }
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept" : "application/json",
            "Authorization" : f"Bearer {session_token}"
        }
        response = requests.post(ipn_url,json=ipn_request_payload,headers=headers)
        
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
        
    