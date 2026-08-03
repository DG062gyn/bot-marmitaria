import requests

GEMINI_API_KEY = "AQ.Ab8RN6IrsXkuScNdc6T3I6_J5uJOcbydI_ePIZTwyMpWMAklDQ"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

PROMPT_SISTEMA = """
Voce e o atendente virtual inteligente da WR Marmitaria.
Seu tom e amigavel, rapido e muito prestativo.

Informacoes do restaurante:
- Cardapio de hoje: Marmita P (RS 18), Marmita M (RS 22), Marmita G (RS 26).
- Opcoes de carne: Frango grelhado, Bife acebolado ou Feijoada.
- Acompanhamentos padrao: Arroz, feijao, farofa e salada.
- Taxa de entrega: RS 5,00 para o bairro local.
- Formas de pagamento: Pix ou Cartao na entrega.

Regras de atendimento:
1. Responda de forma direta e curta (estilo WhatsApp).
2. Se o cliente pedir o cardapio, informe os tamanhos e pratos do dia.
3. Se for fechar pedido, peca: tamanho, opcao de carne, endereco e forma de pagamento.
"""

def responder_cliente(mensagem_usuario):
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "system_instruction": {
            "parts": [{"text": PROMPT_SISTEMA}]
        },
        "contents": [{
            "parts": [{"text": mensagem_usuario}]
        }]
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload)
        dados = response.json()
        
        if "error" in dados:
            return f"Erro na API: {dados['error']['message']}"
            
        return dados["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Erro na requisicao: {e}"

print("--- WR MARMITARIA ---")
while True:
    entrada = input("\nCliente: ")
    if entrada.lower() == "sair":
        break
    resposta = responder_cliente(entrada)
    print(f"\nRobo IA: {resposta}")
