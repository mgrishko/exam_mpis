import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Initialize
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
bot = telebot.TeleBot(API_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Constants
MIN_LEN, MAX_LEN = 50, 4000
LANGUAGES = {
    'uk': 'Ukrainian', 'en': 'English', 'de': 'German', 'fr': 'French',
    'es': 'Spanish', 'it': 'Italian', 'pl': 'Polish', 'ru': 'Russian'
}


# Helpers
def send_error(chat_id, msg_id, text):
    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"❌ {text}")


# Commands
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    text = (
        "👋 *Bot Commands*\n\n"
        "📝 /summarize - Summarize text\n"
        "🌐 /translate - Translate voice\n\n"
        f"Languages: {', '.join(LANGUAGES.keys())}"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['summarize'])
def cmd_summarize(msg):
    bot.send_message(msg.chat.id, f"📝 Send text ({MIN_LEN}-{MAX_LEN} chars):")
    bot.register_next_step_handler(msg, handle_text)


def handle_text(msg):
    text = msg.text.strip()
    
    # Validate
    if len(text) < MIN_LEN:
        bot.reply_to(msg, f"❌ Too short (min {MIN_LEN})")
        return
    if len(text) > MAX_LEN:
        bot.reply_to(msg, f"❌ Too long (max {MAX_LEN})")
        return
    
    # Process
    proc_msg = bot.send_message(msg.chat.id, "⏳ Summarizing...")
    try:
        summary = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Respond ONLY in the same language as input. Create brief summary 20-40% reduction."},
                {"role": "user", "content": f"Summarize:\n\n{text}"}
            ],
            temperature=0.7,
            max_tokens=1000
        ).choices[0].message.content.strip()
        
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=proc_msg.message_id,
            text=f"📝 *Summary:*\n\n{summary}",
            parse_mode="Markdown"
        )
    except Exception as e:
        send_error(msg.chat.id, proc_msg.message_id, str(e))


@bot.message_handler(commands=['translate'])
def cmd_translate(msg):
    bot.send_message(msg.chat.id, "🎤 Send voice:")
    bot.register_next_step_handler(msg, handle_voice)


def handle_voice(msg):
    if not msg.voice:
        bot.reply_to(msg, "❌ Voice message required")
        return
    
    try:
        file_info = bot.get_file(msg.voice.file_id)
        voice_data = bot.download_file(file_info.file_path)
        
        bot.send_message(msg.chat.id, f"🌐 Language: {', '.join(LANGUAGES.keys())}")
        bot.register_next_step_handler(msg, handle_translation, voice_data)
    except Exception as e:
        bot.reply_to(msg, f"❌ {str(e)}")


def handle_translation(msg, voice_data):
    lang = msg.text.strip().lower()
    
    if lang not in LANGUAGES:
        bot.reply_to(msg, f"❌ Invalid. Use: {', '.join(LANGUAGES.keys())}")
        return
    
    proc_msg = bot.send_message(msg.chat.id, "⏳ Translating...")
    
    try:
        # Transcribe
        voice_file = io.BytesIO(voice_data)
        voice_file.name = "audio.ogg"
        original = client.audio.transcriptions.create(
            model="whisper-1",
            file=voice_file
        ).text
        
        # Translate
        translated = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate to {LANGUAGES[lang]}. Only translation."},
                {"role": "user", "content": original}
            ],
            temperature=0.7,
            max_tokens=500
        ).choices[0].message.content.strip()
        
        # Result
        result = f"✅ *Done*\n\n📝 {original}\n\n🌐 {translated}"
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=proc_msg.message_id,
            text=result,
            parse_mode="Markdown"
        )
    except Exception as e:
        send_error(msg.chat.id, proc_msg.message_id, str(e))


# Run
if __name__ == '__main__':
    print("🤖 Bot started...")
    bot.infinity_polling()
