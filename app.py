
from flask import Flask, request, jsonify

app = Flask(__name__)

# Health check
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "running"}), 200


# Webhook endpoint
# Change your_service to the platform name you've been assigned.
@app.route('/webhook/your_service', methods=['POST'])
def webhook():
    try:

        # YOU MAY NEED TO UPDATE THIS SECTION 
        # DEPENDING ON YOUR PLATFORM
        data = request.get_json(silent=True)
        
        if data is None:
            data = request.data.decode('utf-8')

        print("Received webhook:", data)

        # THIS IS WHERE THE CODE TO PROCESS
        # YOUR WEBHOOK WILL GO

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error processing webhook:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


# You will bind your ngrok to this port
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5121, debug=True)

