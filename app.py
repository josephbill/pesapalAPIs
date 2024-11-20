from flask import Flask, request, jsonify,json
import requests
import random
import string
from utils.constants import consumer_key,consumer_secret,base_url


app = Flask(__name__)
# CORS(app)

'''
Client End 
data => amount -> phone number-> email -> onclick of checkout : 
 - post to /get-pesapal-token 
 - on response we save the token info. (local storage , data structure ) 
 - post to /registerIPNURL
 - on response we save the ipn_id info. (local storage , data structure )
 - use the token and ipn_id info to submit a checkout option request (mpesa,airtel money, banking options )
 - Once you get the payment URL , capture the OrderTrackingID from appended URL parameter e.g 
https://cybqa.pesapal.com/pesapaliframe/PesapalIframe3/Index?OrderTrackingId=0b505564-2540-40d9-9cf1-dc7ee98602be
 - in js using the window object capture the orderTrackingID parameter appended to URL 

'''

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
    
    
# after getting the token and ipn_id from above process , we are ready to submit a checkout 
# process for our users 
def generate_random_id(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/submit-order', methods=['POST'])
def submit_order():
    # capture info from client
    submitURL = f"{base_url}/api/Transactions/SubmitOrderRequest" 
    print(submitURL)
    data = request.get_json()
    session_token  = data.get("sessionToken")
    ipn_id = data.get("ipnId")
    # ensure the amount is an integer 
    # 5,000 : clean using str operation substring : 5000
    intAmt = data.get("amount")
    email = data.get("emailCust")
    phone = data.get("phoneCust")
    lname = data.get("lname")
    fname = data.get("fname")
    
    # generate random ids for my transaction 
    transaction_id = generate_random_id()
    print(transaction_id)
    
    # the callback url is used to return transaction info i.e. success or failure from redirect url
    # if success it gives the ordertrackingId and merchantIds
    # a hosted .html page 
    order_request = {
            "id": transaction_id,
            "currency": "KES",
            "amount": intAmt,
            "description": "Payment description goes here",
            "callback_url": "https://lucent-moxie-7b30b4.netlify.app/",
            "redirect_mode": "",
            "notification_id": ipn_id,
            "branch": "Pesapal APIS",
            "billing_address": {
                "email_address": email,
                "phone_number": phone,
                "country_code": "KE",
                "first_name": fname,
                "middle_name": "",
                "last_name": lname,
                "line_1": "Pesapal Limited",
                "line_2": "",
                "city": "",
                "state": "",
                "postal_code": "",
                "zip_code": ""
            }
            
    }  
    print(order_request)
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept" : "application/json",
            "Authorization" : f"Bearer {session_token}"
        }
        response = requests.post(submitURL,headers=headers,json=order_request)
        print(response)
        response.raise_for_status()
        result = response.json()
        print("Pesapal API response:", result)
        
        response.raise_for_status()
        #extract necessary info
        return jsonify({
            "merchant_reference": result.get("merchant_reference"),
            "order_tracking_id" : result.get("order_tracking_id"),
            "redirect_url": result.get("redirect_url")
        }), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500
    
    
    
    # confirming the payment status i.e. did the user actually pay or not ,and save transaction
    # to db. 
@app.route('/get-payment-status', methods=['GET'])
def get_payment_status():
    # get the orderTRacking Id and status token from the request parameters 
    order_tracking_id = request.args.get('orderTrackingId')
    status_token = request.headers.get('Authorization')
    
    # define the status url frm pesapal 
    pesapal_status_url = f"https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
    
    headers = {
        "Authorization" : status_token
    }
    
    try:
        response = requests.get(pesapal_status_url, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(result)
        return jsonify(result), response.status_code
        
    except requests.exceptions.RequestException as e:
        print("error : ", e)
        return jsonify({"error" :str(e)}), 500 


if __name__ == '__main__':
    app.run(port=5000)
        
    