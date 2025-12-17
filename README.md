# Telegram Summary & Translation Bot

A single-file Telegram bot for text summarization, voice translation, image contour detection, and image format conversion using OpenAI APIs and OpenCV.

## Features

- 📝 **Text Summarization** - Summarize text using GPT-3.5-turbo with language preservation
- 🎤 **Voice Translation** - Transcribe voice with Whisper and translate to 8 languages
- 📸 **Contour Detection** - Detect object contours in images using OpenCV
- 🖼️ **Image Conversion** - Convert images between JPEG and PNG formats
- 🇺🇦 🇬🇧 Supports Ukrainian, English, German, French, Spanish, Italian, Polish, Russian

## Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- OpenAI API Key

## Installation

1. Navigate to project folder:
```bash
cd your_project/mpis_exam
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` with your credentials:
```
TELEGRAM_API_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
```

5. Run the bot:
```bash
python bot.py
```

## Commands

- `/start` - Show available commands
- `/summarize` - Summarize text (50-4000 characters)
- `/translate` - Transcribe and translate voice messages
- `/detect` - Detect object contours in images
- `/convert` - Convert image format (JPEG ↔ PNG)
