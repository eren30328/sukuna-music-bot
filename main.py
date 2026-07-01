import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# Render server ko active rakhne ke liye dummy website
app = Flask('')

@app.route('/')
def home():
    return "Sukuna Music Bot is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Telegram Bot Setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN Environment Variable me set nahi hai!")
    import time
    while True:
        time.sleep(10)

bot = telebot.TeleBot(BOT_TOKEN)

# Welcome Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Mujhe kisi bhi gaane ka naam ya YouTube link bhejo, main aapko audio download karke dunga.")

# Music Download Logic
@bot.message_handler(func=lambda message: True)
def download_and_send_audio(message):
    query = message.text
    status_msg = bot.reply_to(message, "🔍 Searching aur processing ho rahi hai... Thoda intezar karein.")
    
    # Bina FFmpeg aur bina YouTube block ke chalne ke liye setup
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube block se bachne ke liye SoundCloud engine use kiya hai
            if "youtube.com" in query or "youtu.be" in query:
                search_query = query
            else:
                search_query = f"scsearch:{query}"
                
            info = ydl.extract_info(search_query, download=True)
            
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            filename = ydl.prepare_filename(video_info)
            
        # Audio file send karna
        with open(filename, 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                caption=f"🎵 {video_info.get('title')}\n\n🤖 Powered by Sukuna Music Bot"
            )
            
        # File send hone ke baad server se delete karna
        if os.path.exists(filename):
            os.remove(filename)
            
        bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error aaya: {str(e)}\n\nKripya gaane ka naam sahi se likhein.", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("Bot is running successfully...")
    bot.infinity_polling()
