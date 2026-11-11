# Banglish Voice Bot 🎤 → 💬

**Speak Bengali. Get Banglish.**

Millions of Bangladeshis text in Banglish (Bengali written in English letters), like
`ami 10 minute e ashchi`. But voice typing tools write Bengali script (`আমি ১০ মিনিটে আসছি`),
so when your hands are busy (driving, cooking, carrying something) you can't send a message the
way you normally write.

This Telegram bot fixes that: send a voice note in Bengali (English words mixed in are fine), and
it replies with natural Banglish text you can copy and send.

> Status: early prototype. This is step 1 of a bigger plan: a Banglish voice keyboard for Android.
> Building in public. Follow along!

## How it works

```
Voice note (Bengali + English)  →  Gemini AI (listens + writes Banglish)  →  Banglish text
                                                                              👍 / 👎 feedback
```

- One AI call: Google Gemini hears the audio and writes it out in casual Banglish.
- The style rules live in [`prompts/banglish_style.md`](prompts/banglish_style.md): common spellings
  (`ami`, `tumi`, `kemon acho`), English words stay English (`meeting`, `late`).
- Every reply has 👍 / 👎 buttons. Ratings are saved to `feedback.csv` to improve the rules.

## Run it yourself

You need Python 3.10+.

1. **Get a Telegram bot token**: open Telegram, message [@BotFather](https://t.me/BotFather),
   send `/newbot`, and copy the token.
2. **Get a Gemini API key**: go to [Google AI Studio](https://aistudio.google.com/) and create a key.
3. **Install and configure**:

   ```bash
   git clone https://github.com/ahriyad1/banglish-voice-bot.git
   cd banglish-voice-bot
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env             # then paste your two keys into .env
   ```

4. **Start the bot**:

   ```bash
   python bot.py
   ```

5. Open your bot in Telegram, press **Start**, hold the mic button and speak.

## Project files

| File | What it does |
| --- | --- |
| `bot.py` | The Telegram bot: receives voice notes, replies, saves feedback |
| `banglish.py` | Sends audio to Gemini and cleans up the answer |
| `prompts/banglish_style.md` | The Banglish spelling and style rules |
| `tests/` | Small tests (`pip install pytest`, then `pytest`) |

## Roadmap

- [x] Telegram bot prototype
- [ ] Test with 20 people, tune the spelling rules from feedback
- [ ] Compare speech engines on real recordings (including road noise)
- [ ] Android keyboard with a one-tap mic button
- [ ] Hands-free mode for drivers

## Feedback

Tried it? Open an [issue](https://github.com/ahriyad1/banglish-voice-bot/issues) with what you said
and what the bot wrote. Every wrong spelling helps.
