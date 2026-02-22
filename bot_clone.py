import telebot
import requests
import json
import hashlib
import time
import os
import random
from flask import Flask
from threading import Thread

# --- SERVIDOR PARA O RENDER NÃO DESLIGAR ---
app = Flask('')

@app.route('/')
def home():
    return "Robô Shopee VIP Online! 🚀💰"

def run_server():
    # O Render exige que o servidor rode na porta definida pela variável de ambiente PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- CONFIGURAÇÕES DO ROBÔ ---
TOKEN = "8450495026:AAFsdEmkkRRJAW-Fp8QqtGlQZ16eSrq4WG4"
APP_ID = "18384670408"
SECRET = "Z3UIVKU5Q2PJHSFMFIZFD2G6LDJG2EBG"
CHAT_ID = "-1003777686760"
API_URL = "https://open-api.affiliate.shopee.com.br/graphql"

bot = telebot.TeleBot(TOKEN)
produtos_postados = []

def get_signature(payload, timestamp):
    sign_str = f"{APP_ID}{timestamp}{payload}{SECRET}"
    return hashlib.sha256(sign_str.encode("utf-8")).hexdigest()

def buscar_e_postar_ofertas():
    global produtos_postados
    palavras = ["fone bluetooth", "relogio masculino", "utilidades cozinha", "maquiagem", "eletronicos", "moda feminina", "acessorios celular", "brinquedos", "decoracao casa", "ferramentas", "pet shop"]
    random.shuffle(palavras) 
    contador_de_posts = 0
    
    for termo in palavras:
        print(f"🔎 Buscando: {termo}...")
        timestamp = int(time.time())
        query = f'{{productOfferV2(keyword: "{termo}", limit: 10){{nodes{{productName,imageUrl,priceMin,productLink}}}}}}'
        payload = json.dumps({"query": query}, separators=(",", ":"))
        sig = get_signature(payload, timestamp)
        headers = {"Authorization": f"SHA256 Credential={APP_ID}, Timestamp={timestamp}, Signature={sig}", "Content-Type": "application/json"}
        
        try:
            r = requests.post(API_URL, headers=headers, data=payload).json()
            produtos = r.get("data", {}).get("productOfferV2", {}).get("nodes", [])
            if not produtos: continue

            postou_neste_termo = False
            for p in produtos:
                if postou_neste_termo: break
                nome_produto = p['productName']
                if nome_produto in produtos_postados: continue
                
                ts_l = int(time.time())
                url_original = p['productLink'].split('?')[0]
                q_l = 'mutation{generateShortLink(input:{originUrl:"%s"}){shortLink}}' % url_original
                p_l = json.dumps({"query": q_l}, separators=(',', ':'))
                sig_l = get_signature(p_l, ts_l)
                h_l = {"Authorization": f"SHA256 Credential={APP_ID}, Timestamp={ts_l}, Signature={sig_l}", "Content-Type": "application/json"}
                
                r_l = requests.post(API_URL, headers=h_l, data=p_l).json()
                link_final = r_l.get("data", {}).get("generateShortLink", {}).get("shortLink")

                if link_final and ("shope.ee" in link_final or "s.shopee" in link_final):
                    msg = (f"🎁 *NOVIDADE COM DESCONTO NO CANAL!* 🎁\n\n📦 *{p['productName'][:100]}...*\n\n✅ *POR APENAS: R$ {float(p['priceMin']):.2f}*\n\n🔥 *PROMOÇÃO EXCLUSIVA:* \n👉 [CLIQUE AQUI E CONFIRA]({link_final})\n\n🏃‍♂️💨 *APROVEITE:* O estoque é limitado! ✨")
                    bot.send_photo(CHAT_ID, p['imageUrl'], caption=msg, parse_mode="Markdown")
                    print(f"✅ Postado: '{termo}'")
                    produtos_postados.append(nome_produto)
                    if len(produtos_postados) > 50: produtos_postados.pop(0)
                    postou_neste_termo = True
                    contador_de_posts += 1
                    if contador_de_posts % 2 == 0:
                        time.sleep(60) 
                    else:
                        time.sleep(10) 
        except Exception as e:
            print(f"❌ Erro em '{termo}': {e}")

# --- INÍCIO ---
if __name__ == "__main__":
    keep_alive() # Inicia o servidor para o Render
    print("🚀 Robô VIP v25 (RENDER 24H) Online!")
    while True:
        buscar_e_postar_ofertas()
        print("☕ Ciclo concluído. Aguardando 3 minutos...")
        time.sleep(180)
        
