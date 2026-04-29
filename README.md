# 🤖 Telegram Reminder Bot — Smart Arabic/English NLP Scheduler

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.x-blue)](https://python-telegram-bot.org)
[![Google Tasks API](https://img.shields.io/badge/Google%20Tasks%20API-v1-4285F4?logo=google)](https://developers.google.com/tasks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade Telegram bot that understands **natural language reminders** in Arabic and English, extracts dates intelligently, and syncs them to **Google Tasks / Google Calendar** via OAuth 2.0.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🌍 **Bilingual NLP** | Understands Arabic & English date expressions natively |
| 📅 **Smart Date Parsing** | Handles "الأحد المقبل", "next Monday", "غداً الساعة 9" |
| 🔐 **Secure OAuth 2.0** | Per-user Google account linking, tokens stored securely |
| ✅ **Google Tasks Sync** | Creates tasks with due dates in user's default task list |
| 📆 **Calendar Support** | Optional Google Calendar event creation |
| ⚡ **Fully Async** | Built on `python-telegram-bot` v20 async architecture |

---

## 🗂️ Project Structure

```
telegram-reminder-bot/
├── main.py                  # Entry point — starts the bot
├── demo.py                  # Standalone NLP demo (no Telegram token needed)
├── requirements.txt
├── .env.example
│
├── bot/                     # Telegram layer
│   ├── handlers.py          # Command & message handlers
│   └── keyboards.py         # Inline keyboard builders
│
├── nlp/                     # NLP / date extraction layer
│   ├── parser.py            # ReminderParser — main parsing engine
│   └── arabic_patterns.py   # Arabic regex patterns & keyword maps
│
├── services/                # External API integrations
│   ├── oauth.py             # Google OAuth 2.0 flow
│   ├── google_tasks.py      # Google Tasks API v1 client
│   └── google_calendar.py   # Google Calendar API client
│
├── config/
│   └── settings.py          # Pydantic-settings config (loads .env)
│
├── utils/
│   ├── logger.py            # Structured logging setup
│   └── helpers.py           # Shared utility functions
│
└── tests/
    └── test_parser.py       # Unit tests for NLP parser
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/telegram-reminder-bot.git
cd telegram-reminder-bot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Fill in your tokens:
nano .env
```

### 3. Test the NLP Parser (no bot token needed)

```bash
python demo.py
```

### 4. Run the Bot

```bash
python main.py
```

---

## 🔧 Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_BotFather
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_REDIRECT_URI=https://your-domain.com/oauth/callback
TIMEZONE=Asia/Riyadh
```

---

## 🔐 Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Google Tasks API** and **Google Calendar API**
3. Create **OAuth 2.0 credentials** (Web Application type)
4. Add your `OAUTH_REDIRECT_URI` to authorized redirect URIs
5. Copy `Client ID` and `Client Secret` to your `.env`

> **Scopes used:**
> - `https://www.googleapis.com/auth/tasks`
> - `https://www.googleapis.com/auth/calendar.events`

---

## 💬 Usage Examples

Send any of these to the bot:

```
ذكرني بموعد الطبيب الأحد المقبل الساعة 9 مساءً
ذكرني بدفع الإيجار غداً الساعة 10 صباحاً
Remind me to call Ahmed next Monday at 3 PM
Remind me about the team standup tomorrow at 9:30 AM
```

---

## 🧠 NLP Architecture

```
User Message
     │
     ▼
Arabic Normalizer      ← replaces "الأحد المقبل" → "next Sunday"
     │                    replaces "مساءً" → "PM"
     ▼
dateparser.parse()     ← multilingual date extraction engine
     │                    settings: PREFER_DATES_FROM=future
     ▼
ParsedReminder         ← { title, datetime_obj, confidence }
     │
     ▼
Google Tasks API       ← creates task with RFC 3339 due date
```

---

## 🤝 Contributing

PRs welcome! Please open an issue first for major changes.

---

## 📄 License

MIT © 2024
