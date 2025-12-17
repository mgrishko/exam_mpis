import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv
import io
import cv2
import numpy as np
from PIL import Image

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


def detect_contours(image_data):
    """Detect object contours using OpenCV"""
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on image
    result = img.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
    
    # Encode result image
    _, buffer = cv2.imencode('.jpg', result)
    
    return buffer.tobytes(), len(contours)


def convert_image_format(image_data, target_format):
    """Convert image format using Pillow"""
    img = Image.open(io.BytesIO(image_data))
    
    # Convert RGBA to RGB for JPEG
    if target_format.upper() == 'JPEG' and img.mode == 'RGBA':
        img = img.convert('RGB')
    
    output = io.BytesIO()
    img.save(output, format=target_format.upper())
    output.seek(0)
    return output.getvalue()


# Commands
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    text = (
        "👋 *Bot Commands*\n\n"
        "📝 /summarize - Summarize text\n"
        "🌐 /translate - Translate voice\n"
        "📸 /detect - Detect contours\n"
        "📸 /convert - Convert image (JPEG ↔ PNG)\n\n"
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


@bot.message_handler(commands=['convert'])
def cmd_convert(msg):
    bot.send_message(msg.chat.id, "📸 Send image to convert:")
    bot.register_next_step_handler(msg, handle_convert_image)


def handle_convert_image(msg):
    if not msg.photo:
        bot.reply_to(msg, "❌ Image required")
        return
    
    try:
        file_info = bot.get_file(msg.photo[-1].file_id)
        image_data = bot.download_file(file_info.file_path)
        
        bot.send_message(msg.chat.id, "📁 Format? (JPEG or PNG):")
        bot.register_next_step_handler(msg, handle_target_format, image_data)
    except Exception as e:
        bot.reply_to(msg, f"❌ {str(e)}")


def handle_target_format(msg, image_data):
    target_format = msg.text.strip().upper()
    
    if target_format not in ['JPEG', 'PNG']:
        bot.reply_to(msg, "❌ Use: JPEG or PNG")
        return
    
    proc_msg = bot.send_message(msg.chat.id, "⏳ Converting...")
    
    try:
        result_data = convert_image_format(image_data, target_format)
        result_file = io.BytesIO(result_data)
        result_file.name = f"converted.{target_format.lower()}"
        
        bot.delete_message(msg.chat.id, proc_msg.message_id)
        bot.send_document(msg.chat.id, result_file, caption=f"✅ Converted to {target_format}")
    except Exception as e:
        send_error(msg.chat.id, proc_msg.message_id, str(e))


@bot.message_handler(commands=['detect'])
def cmd_detect(msg):
    bot.send_message(msg.chat.id, "📸 Send image to detect contours:")
    bot.register_next_step_handler(msg, handle_image)


def handle_image(msg):
    if not msg.photo:
        bot.reply_to(msg, "❌ Image required")
        return
    
    proc_msg = bot.send_message(msg.chat.id, "⏳ Detecting contours...")
    
    try:
        file_info = bot.get_file(msg.photo[-1].file_id)
        image_data = bot.download_file(file_info.file_path)
        
        # Detect contours
        result_image, count = detect_contours(image_data)
        
        # Send result
        result_file = io.BytesIO(result_image)
        result_file.name = "contours.jpg"
        
        bot.delete_message(msg.chat.id, proc_msg.message_id)
        bot.send_photo(
            msg.chat.id,
            result_file,
            caption=f"✅ Found {count} contours"
        )
    except Exception as e:
        send_error(msg.chat.id, proc_msg.message_id, str(e))
if __name__ == '__main__':
    print("🤖 Bot started...")
    bot.infinity_polling()
