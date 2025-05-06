from flask import Blueprint, jsonify, render_template, request
import openai
import requests
import os
from flask_login import login_required
from models.conversation import Conversation
from models.bot_setting import BotSetting
from models import db
from datetime import datetime

main_bp = Blueprint('main', __name__)


openai.api_key = os.getenv("OPENAI_API_KEY")
GUPSHUP_API = os.getenv("GUPSHUP_API")
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.getenv("GUPSHUP_SOURCE")
GUPSHUP_APP_NAME = os.getenv("GUPSHUP_APP_NAME")


def openaiService(message):
    try:
        setting = BotSetting.query.first()  # Fetch the first settings

        SYSTEM_PROMPT = f"""
            Você é um assistente virtual da {setting.site_name}. Seu objetivo é responder às perguntas dos clientes sobre nossos serviços, preços, horário de funcionamento, endereço, delivery e outras informações relevantes sobre a lavanderia. Use SOMENTE as informações fornecidas abaixo para basear suas respostas. Seja cordial, prestativo e responda em português brasileiro.

            --- INFORMAÇÕES DA {setting.site_name} ---

            **1. Sobre a Lavanderia**
            {setting.service_description}

            **2. Endereço e Horário de Funcionamento**
            {setting.business_time}

            **3. Delivery (Coleta e Entrega)**
            {setting.delivery}

            **4. Lista de Preços**

            {setting.service_price}

            --- FIM DAS INFORMAÇÕES ---

            Instruções Adicionais:
            - Responda apenas com base nas informações fornecidas acima.
            - Se a pergunta for sobre um serviço ou item não listado (por exemplo, "lavagem de cortinas"), informe que você não tem informações sobre esse serviço específico e sugira entrar em contato pelo telefone 11 93774-4626 para verificar a disponibilidade. Também, Nestes casos, recomende entrar em contato diretamente pelo WhatsApp neste link: https://wa.me/message/L4TBXL2ZK3T7I1.
            - Se perguntarem sobre a área de entrega, mencione as áreas cobertas e a taxa, e sempre peça o CEP para confirmação.
            - Mantenha as respostas claras e objetivas.
            - Não invente informações ou preços.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )
        reply_text = response.choices[0].message.content
        return {"result": reply_text}

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
    saveMessage(GUPSHUP_SOURCE, phone_number, message)


def saveMessage(phone_from, phone_to, message):
    if not phone_from or not phone_to or not message:
        print("Missing required fields")
        return 'Missing required fields'
    
    # Create a new conversation object
    new_conversation = Conversation(
        phone_from=phone_from,
        phone_to=phone_to,
        message=message,
        created_at=datetime.now()  # Use the current timestamp
    )

    # Add the new conversation to the session and commit to save it in the database
    db.session.add(new_conversation)
    db.session.commit()


@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')


processed_message_ids = set()

@main_bp.route("/webhook", methods=["POST", "HEAD"])
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
                    message_id = msg.get("id")

                    # Skip if already processed
                    if message_id in processed_message_ids:
                        print(f"Skipping duplicate message ID: {message_id}")
                        continue

                    processed_message_ids.add(message_id)

                    sender = msg.get("from")  # WhatsApp number
                    text = msg.get("text", {}).get("body")
                    
                    print(f"Message from {sender}: {text}: ", msg)
                    print(f"contacts => ", contacts)
                    print(f"value => ", value)

                    saveMessage(sender, GUPSHUP_SOURCE, text)

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
