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
    
    # try:
    #     data = request.get_json()
    #     print("Webhook received:", data)
    #     message = data["payload"]["payload"]["text"]
    #     user_phone = data["payload"]["sender"]["phone"]

    #     if not message or not user_phone:
    #         return jsonify({"status": "ignored", "reason": "Missing text or phone"}), 200

    #     # Send to ChatGPT
    #     response = openai.chat.completions.create(
    #         model="gpt-4",
    #         messages=[
    #             {"role": "system", "content": "You are a helpful assistant for a safirabusiness business."},
    #             {"role": "user", "content": message}
    #         ]
    #     )
    #     print('chatgpt response: ', response)
    #     reply_text = response.choices[0].message.content

    #     # Send reply via Gupshup
    #     payload = {
    #         "channel": "whatsapp",
    #         "source": GUPSHUP_SOURCE,
    #         "destination": user_phone,
    #         "message": reply_text,
    #         "src.name": GUPSHUP_APP_NAME
    #     }
    #     headers = {
    #         "apikey": GUPSHUP_API_KEY,
    #         "Content-Type": "application/x-www-form-urlencoded"
    #     }
    #     requests.post(GUPSHUP_API, data=payload, headers=headers)

    #     return jsonify({"status": "success"}), 200
    # except Exception as e:
    #     print("Error:", e)
    #     return jsonify({"error": str(e)}), 500

    try:
        data = request.get_json()
        print("Webhook received:", data)

        # Gupshup sometimes sends messages and sometimes status updates
        # Navigate to message content
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

                    # Send reply via Gupshup
                    payload = {
                        "channel": "whatsapp",
                        "source": GUPSHUP_SOURCE,
                        "destination": sender,
                        "message": text,
                        "src.name": GUPSHUP_APP_NAME
                    }
                    headers = {
                        "apikey": GUPSHUP_API_KEY,
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    requests.post(GUPSHUP_API, data=payload, headers=headers)
                    # Reply logic can go here
        return "OK", 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/test", methods=["GET"])
def test():
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a safirabusiness business."},
                {"role": "user", "content": "I am Dmytro Markitan. I want to know about hostinger."}
            ]
        )
        print('response: ', response)
        reply_text = response.choices[0].message.content
        return reply_text
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
