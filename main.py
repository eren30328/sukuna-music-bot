import telebot
import yt_dlp
import os

# Render environment variable se token uthayega
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Mujhe kisi bhi gaane ka naam ya YouTube link bhejo, main aapko MP3 download karke dunga.")

@bot.message_handler(func=lambda message: True)
def download_and_send_audio(message):
    query = message.text
    status_msg = bot.reply_to(message, "🔍 Searching aur processing ho rahi hai... Thoda intezar karein.")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            video_info = info['entries'] if 'entries' in info else info
            filename = ydl.prepare_filename(video_info).replace(video_info['ext'], 'mp3')
            
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption=f"🎵 {video_info.get('title')}\n\n🤖 Powered by Sukuna Music Bot")
            
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error aaya: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
