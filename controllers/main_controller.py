from flask import Blueprint, render_template, request
import openai
import requests
import os
from dateutil import parser
from flask_login import login_required

main_bp = Blueprint('main', __name__)


openai.api_key = os.getenv("OPENAI_API_KEY")
GUPSHUP_API = os.getenv("GUPSHUP_API")
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")
GUPSHUP_SOURCE = os.getenv("GUPSHUP_SOURCE")
GUPSHUP_APP_NAME = os.getenv("GUPSHUP_APP_NAME")

# Function to detect if a message is about scheduling or just mentioning a date
def detect_schedule_intent(message):
    # Keywords that indicate scheduling
    scheduling_keywords = ["schedule", "pickup", "delivery", "collect", "appointment", "reserve"]
    
    # Check if the message contains any scheduling-related keywords
    if any(keyword in message.lower() for keyword in scheduling_keywords):
        return True
    return False

def detect_datetime(message):
    try:
        # Attempt to parse the input text
        parsed_date = parser.parse(message, fuzzy=True)
        return parsed_date
    except ValueError:
        return None

def openaiService(message):
    try:
        SYSTEM_PROMPT = """
            Você é um assistente virtual amigável e profissional para a Lavanderia Safira, referência em qualidade há mais de 10 anos. 
            Atendemos Taboão da Serra e região, com serviços de lavagem de roupas, tapetes, higienização de estofados e muito mais.

            Aqui estão as informações que você pode usar para responder aos clientes:
            1. **Sobre a Lavanderia**:
            "Somos a Lavanderia Safira, referência em qualidade há mais de 10 anos! Atendemos Taboão da Serra e região, com serviços de lavagem de roupas, tapetes, higienização de estofados e muito mais."

            2. **Endereço e Horário de Funcionamento**:
            "Nossa loja fica na Estrada San Francisco, 1857 — Jardim Henriqueta, Taboão da Serra/SP.
            Horário de funcionamento:
            • Segunda a sexta: 8h às 18h
            • Sábado: 9h às 13h
            (Fechado aos domingos e feriados)."

            3. **Serviço de Delivery (Coleta e Entrega)**:
            "Oferecemos serviço de coleta e entrega para:
            • Taboão da Serra
            • Algumas áreas da Zona Sul de São Paulo (próximas ao Campo Limpo e arredores)
            • Embu das Artes.

            Taxa única de R$10,00, incluindo retirada e entrega.
            Coletas acontecem às terças, quartas e sextas-feiras, entre 8h30 e 17h30.
            Envie seu CEP para verificarmos se atendemos a sua região!"

            4. **Agendamento de Coleta**:
            Quando o cliente solicitar o agendamento de uma coleta:
            - Solicite o **CEP** para verificar se a região é atendida.
            - Pergunte a **data** e **hora** preferidas para a coleta (considerando os dias disponíveis).
            - Confirme a coleta e registre os detalhes de agendamento (em um banco de dados ou outra solução de armazenamento).

            5. **Compreendendo Datas no Contexto de Agendamentos**:
            - Quando o cliente fornecer uma data ou hora, verifique se está relacionado ao agendamento de uma coleta. Se palavras como "agendar", "coleta", "entrega", "retirar" aparecerem, interprete como um pedido de agendamento.
            - Se o cliente mencionar uma data sem essas palavras-chave (por exemplo, "Tenho uma reunião na segunda-feira" ou "Meu aniversário é no dia 5"), não trate como um pedido de agendamento.
            - Se a intenção não estiver clara, pergunte ao cliente: "Você está se referindo a agendar uma coleta ou apenas mencionando uma data?"

            Sempre responda de forma amigável e forneça informações sobre os serviços, localização, horários e a área de entrega. Caso o cliente queira agendar uma coleta, peça o CEP e confirme a disponibilidade da região.
        """

        # Check if the message contains a scheduling-related date
        if detect_schedule_intent(message):
            # Extract and confirm the date/time for scheduling
            date_time = detect_datetime(message)
            if date_time:
                return {"result": f"Collection scheduled for {date_time.strftime('%A, %B %d, %Y at %I:%M %p')}"}
            else:
                return {"result": "Could you please provide a specific date and time for the collection?"}
        else:
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



@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

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
