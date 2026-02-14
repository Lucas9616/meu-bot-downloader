import logging
import os
import re
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 **Seu Assistente de Vendas Shopee está ON!**\n\n"
        "1. Gere seu link de afiliado no App da Shopee.\n"
        "2. Cole o link aqui.\n"
        "3. Eu baixo o vídeo e monto o post pronto para o seu canal! 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    urls = re.findall(r'(https?://\S+)', text)
    if not urls: return
    url = urls[0]

    status_message = await update.message.reply_text("🎬 Baixando vídeo do produto... Aguarde.")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).prepare_filename(yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)))
            
        if os.path.exists(file_path):
            # Botão com o SEU link de afiliado que você enviou
            keyboard = [[InlineKeyboardButton("🛒 COMPRAR AGORA", url=url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(file_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file, 
                    caption=f"🛍️ **ACHADINHO DO DIA!**\n\n✨ Olha que incrível esse produto que encontrei!\n\n🚚 Frete Grátis disponível!\n\n👇 **CLIQUE NO LINK ABAIXO PARA COMPRAR:**\n{url}",
                    reply_markup=reply_markup
                )
            os.remove(file_path)
            await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text("❌ Erro ao baixar o vídeo. Tente enviar o link novamente.")

if __name__ == '__main__':
    TOKEN = "8296337973:AAFzThCZX4A7bj9BKFtSwd0cZpglOUl2PKY"
    os.makedirs("downloads", exist_ok=True)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
    
