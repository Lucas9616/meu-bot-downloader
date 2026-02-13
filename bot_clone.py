import logging
import os
import re
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Regex abrangente para plataformas
SHOPEE_REGEX = r'(shopee\.com\.br|shope\.ee|shp\.ee)'
TIKTOK_REGEX = r'(tiktok\.com)'
INSTAGRAM_REGEX = r'(instagram\.com)'
PINTEREST_REGEX = r'(pinterest\.com|pin\.it)'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Eu sou o seu Downloader de Vídeos.\n\n"
        "🚀 Envie um link do **TikTok, Instagram, Pinterest ou Shopee Vídeo** e eu farei o download para você!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    urls = re.findall(r'(https?://\S+)', text)
    if not urls:
        return
    
    url = urls[0]

    if any(re.search(pattern, url) for pattern in [SHOPEE_REGEX, TIKTOK_REGEX, INSTAGRAM_REGEX, PINTEREST_REGEX]):
        status_message = await update.message.reply_text("⏳ Analisando link e preparando download...")
        
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            }
            
            loop = asyncio.get_event_loop()
            
            def download_video(v_url):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(v_url, download=True)
                    return ydl.prepare_filename(info)

            file_path = await loop.run_in_executor(None, download_video, url)
                
            if os.path.exists(file_path):
                with open(file_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file, 
                        caption="✅ Vídeo baixado com sucesso!",
                        supports_streaming=True
                    )
                os.remove(file_path)
                await status_message.delete()
            else:
                await status_message.edit_text("❌ Erro ao localizar o arquivo.")
            
        except Exception as e:
            await status_message.edit_text("❌ Não consegui baixar este vídeo. Tente outro link.")
    else:
        pass

if __name__ == '__main__':
    # Use o seu Token aqui
    TOKEN = "8296337973:AAFzThCZX4A7bj9BKFtSwd0cZpglOUl2PKY"
    os.makedirs("downloads", exist_ok=True)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
