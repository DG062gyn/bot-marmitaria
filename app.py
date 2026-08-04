import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

# Configurações de Variáveis de Ambiente
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EVOLUTION_URL = os.environ.get("EVOLUTION_URL")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY")
EVOLUTION_INSTANCE_NAME = os.environ.get("EVOLUTION_INSTANCE_NAME", "marmitaria")

# Configura o SDK do Gemini com a API Key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

PROMPT_SISTEMA = """
Voce e o atendente virtual inteligente da WR Marmitaria.
Seu tom e amigavel, rapido e muito prestativo.

Informacoes do restaurante:
- Cardapio de hoje: Marmita P (R$ 18), Marmita M (R$ 22), Marmita G (R$ 25).
- Opcoes de carne: Frango grelhado, Bife acebolado, Peixe frito.
- Acompanhamentos padrao: Arroz, feijao, farofa e salada.
- Taxa de entrega: R$ 5,00 para o bairro local.
- Formas de pagamento: Pix ou Cartao na entrega.

Regras de atendimento:
1. Responda de forma direta e curta.
2. Se o cliente pedir o cardapio, informe os tamanhos e opcoes.
3. Se for fechar pedido, peca: tamanho, opcao de carne, endereco e forma de pagamento.
"""

def responder_cliente(mensagem_usuario):
    try:
        # Usa o modelo gemini-1.5-flash corrigido com System Instruction
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=PROMPT_SISTEMA
        )
        response = model.generate_content(mensagem_usuario)
        return response.text
    except Exception as e:
        print(f"Erro na chamada do Gemini: {e}")
        return "Desculpe, tive uma instabilidade momentânea aqui no sistema! Pode repetir a sua mensagem, por favor?"

def enviar_mensagem_whatsapp(remote_jid, texto):
    """Envia a resposta de volta para o cliente via Evolution API"""
    if not EVOLUTION_URL or not EVOLUTION_API_KEY:
        print("Erro: Variáveis da Evolution API não foram configuradas.")
        return

    url_envio = f"{EVOLUTION_URL.strip('/')}/message/sendText/{EVOLUTION_INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    payload = {
        "number": remote_jid,
        "text": texto
    }
    try:
        response = requests.post(url_envio, headers=headers, json=payload, timeout=10)
        print(f"Status Evolution: {response.status_code} - Resposta: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem no WhatsApp: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json() or {}

    try:
        # Verifica se é uma mensagem recebida do WhatsApp
        event = data.get("event")
        if event == "messages.upsert":
            message_data = data.get("data", {})
            key = message_data.get("key", {})
            
            # Garante que não responde a mensagens enviadas pelo próprio bot
            from_me = key.get("fromMe", False)
            if not from_me:
                remote_jid = key.get("remoteJid")
                
                # Extrai o texto enviado pelo cliente
                message = message_data.get("message", {})
                texto_cliente = message.get("conversation") or message.get("extendedTextMessage", {}).get("text", "")

                if texto_cliente:
                    # Gera a resposta via Gemini
                    resposta_ia = responder_cliente(texto_cliente)
                    
                    # Envia de volta para o WhatsApp do cliente
                    enviar_mensagem_whatsapp(remote_jid, resposta_ia)

    except Exception as e:
        print(f"Erro no processamento do Webhook: {e}")

    return jsonify({"status": "SUCCESS"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
