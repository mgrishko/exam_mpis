# Telegram Summary & Translation Bot

A single-file Telegram bot with two core features: text summarization and voice translation using OpenAI APIs.

## Features

- 📝 **Text Summarization** - Create concise summaries of any text using GPT-3.5-turbo (30-50% reduction)
- 🎤 **Voice Translation** - Transcribe voice messages with Whisper and translate to 8 different languages
- 🇺🇦 🇬🇧 Supports Ukrainian, English, German, French, Spanish, Italian, Polish, Russian
- ⚡ Fast and clean refactored code with only 2 main endpoints
- 🛡️ Error handling and input validation

## Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- OpenAI API Key

## Installation

1. Clone the repository or navigate to project folder:
```bash
cd /Users/mgrishko/study/mpis_exam
```

2. Create and activate virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your credentials:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```
TELEGRAM_API_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
```

## How to Get Credentials

### Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create a new bot
4. Copy the API token

### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Sign up or log in
3. Set up billing (required for API access)
4. Create a new API key
5. Copy it to your `.env` file

## Running the Bot

```bash
python bot.py
```

The bot will run and listen for incoming messages indefinitely. Press `Ctrl+C` to stop.

## Usage

### Text Summarization

1. Send `/summarize` command
2. Send text you want to summarize (50-4000 characters)
3. Bot will create and send summary (30-50% reduction)

Example:
```
/summarize
LongLongText...
```

### Voice Translation

1. Send `/translate` command
2. Send a voice message
3. Choose target language code: `uk`, `en`, `de`, `fr`, `es`, `it`, `pl`, `ru`
4. Bot will transcribe and translate the message

Example:
```
/translate
[send voice message]
en
```

## Commands

- `/start` - Show welcome message
- `/summarize` - Start text summarization
- `/translate` - Start voice translation

## How It Works

### Text Summarization
1. User sends text via `/summarize` command
2. Text is validated (50-4000 characters)
3. OpenAI GPT-3.5-turbo creates summary
4. Summary text is returned (30-50% reduction)

### Voice Translation
1. User sends voice message via `/translate` command
2. OpenAI Whisper API transcribes voice to text
3. User selects target language
4. GPT-3.5-turbo translates text to target language
5. Both original and translated text are returned

## File Structure

```
.
├── bot.py              # Main bot file (single file)
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env               # Environment variables (not in git)
└── README.md          # This file
```

## Cost Considerations

- **Text Summarization**: Uses OpenAI GPT-3.5-turbo (cheap)
- **Voice Translation**: Uses Whisper API (cheap) + GPT-3.5-turbo
- Monitor usage at: https://platform.openai.com/usage
- Set up billing limits to avoid unexpected charges

## Error Handling

The bot includes error handling for:
- Text length validation (50-4000 characters)
- Invalid language codes
- Voice file download errors
- OpenAI API errors and timeouts
- Network connectivity issues

## Limitations

- Maximum text length: 4000 characters
- Text must be 50+ characters for summarization
- Voice translation requires valid language code
- Each request uses OpenAI API tokens (costs apply)

## Troubleshooting

### Bot doesn't respond
- Check if API token is correct in `.env`
- Verify bot is running with `python bot.py`
- Check bot has Internet connection

### "Error during processing"
- Verify OpenAI API key is valid
- Check OpenAI billing is set up
- Ensure API key has sufficient balance

### Voice translation not working
- Send voice message in clear language
- Ensure Whisper model can understand the language
- Try with shorter voice messages

## License

Free to use and modify.

## Support

For issues or questions, check:
- OpenAI documentation: https://platform.openai.com/docs
- Telegram Bot API: https://core.telegram.org/bots
- pyTelegramBotAPI: https://github.com/eternnoir/pyTelegramBotAPI
