from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import requests
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
GUPSHUP_API = os.getenv("GUPSHUP_API")
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.getenv("GUPSHUP_SOURCE")
GUPSHUP_APP_NAME = os.getenv("GUPSHUP_APP_NAME")

app = Flask(__name__)

def openaiService(message):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a friendly and professional chatbot for a local laundromat called FreshSpin. Answer customer questions about services, pricing, pickup & delivery, and machine availability. Keep your replies short, helpful, and warm."},
                {"role": "user", "content": message}
            ]
        )
        reply_text = response.choices[0].message.content
        return { "result": reply_text }
    except Exception as e:
        return { "error": str(e) }


# Send reply via Gupshup
def send_whatsapp_reply(phone_number, message):
    headers = {
        "apikey": GUPSHUP_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "channel": "whatsapp",
        "source": GUPSHUP_SOURCE,
        "destination": phone_number,
        "message": message,
        "src.name": GUPSHUP_APP_NAME
    }
    response = requests.post(GUPSHUP_API, headers=headers, data=payload)
    print('response => ', response)
    print("Sent:", response.status_code, response.text)
    print("Sending to:", phone_number)
    print("Message:", message)
    print("Source:", GUPSHUP_SOURCE)
    print("App name:", GUPSHUP_APP_NAME)
    print("Headers:", headers)
    print("Payload:", payload)


@app.route("/", methods=["GET"])
def home():
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/html"
    }
    html = """
    <!DOCTYPE html>
        <html lang="en">
            <head>
                <title>LaundryBot</title>
                <meta charset="UTF-8">
                <meta name="description" content="LaundryBot Assistant for WhatsApp">
            </head>
            <body>
                <h1>Webhook Active</h1>
                <p>This domain is hosting a smart WhatsApp chatbot using OpenAI.</p>
            </body>
        </html>
    """
    return html, 200, headers

@app.route("/webhook", methods=["POST", "HEAD"])
def webhook():
    if request.method == "HEAD":
        return "", 200
    
    try:
        data = request.get_json()
        print("Webhook received:", data)

        # Gupshup sometimes sends messages and sometimes status updates
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])

                if messages:
                    msg = messages[0]
                    sender = msg.get("from")  # WhatsApp number
                    text = msg.get("text", {}).get("body")
                    
                    print(f"Message from {sender}: {text}: ", msg)
                    print(f"contacts => ", contacts)
                    print(f"value => ", value)

                    res = openaiService(text)

                    if "error" in res:
                        print("Error:", res["error"])
                    else:
                        print("AI Response:", res["result"])
                        send_whatsapp_reply(sender, res["result"])

        return "OK", 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
