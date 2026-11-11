"""Telegram bot: send a Bengali voice note, get Banglish text back.

Run:  python bot.py
"""

import asyncio
import csv
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

from banglish import voice_to_banglish  # noqa: E402  (needs .env loaded first)

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("banglish-bot")
# httpx logs every request URL, which contains the bot token. Keep it quiet.
logging.getLogger("httpx").setLevel(logging.WARNING)

FEEDBACK_FILE = Path(os.getenv("FEEDBACK_FILE", "feedback.csv"))
MAX_SECONDS = int(os.getenv("MAX_VOICE_SECONDS", "120"))

# Results waiting for a thumbs up / down, keyed by a short id.
_pending: dict[str, dict] = {}

WELCOME = (
    "Assalamu alaikum! Ami Banglish Voice Bot.\n\n"
    "Bangla te ekta voice message pathan, ami Banglish e likhe dibo.\n"
    "Example: apni bolben \"ami 10 minute e ashchi\" -> ami likhbo: ami 10 minute e ashchi\n\n"
    "Prottek result er niche 👍 / 👎 diye janaben thik hoyeche kina. Eta amake better korte help kore."
)


def feedback_buttons(result_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("👍 Thik ache", callback_data=f"up:{result_id}"),
            InlineKeyboardButton("👎 Vul", callback_data=f"down:{result_id}"),
        ]]
    )


def save_feedback(row: dict) -> None:
    new_file = not FEEDBACK_FILE.exists()
    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["time_utc", "user_id", "rating", "seconds", "latency_s", "text"]
        )
        if new_file:
            writer.writeheader()
        writer.writerow(row)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    media = update.message.voice or update.message.audio
    if media is None:
        return
    if media.duration and media.duration > MAX_SECONDS:
        await update.message.reply_text(f"Doya kore {MAX_SECONDS} second er choto message pathan.")
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    started = time.monotonic()
    try:
        tg_file = await media.get_file()
        audio = bytes(await tg_file.download_as_bytearray())
        mime = getattr(media, "mime_type", None) or "audio/ogg"
        # The AI call is blocking, so run it off the main loop.
        text = await asyncio.to_thread(voice_to_banglish, audio, mime)
    except Exception:
        log.exception("Failed to convert voice note")
        await update.message.reply_text("Sorry, ekta problem hoyeche. Abar try korun.")
        return

    latency = round(time.monotonic() - started, 2)
    result_id = uuid.uuid4().hex[:10]
    _pending[result_id] = {
        "user_id": update.effective_user.id,
        "seconds": media.duration,
        "latency_s": latency,
        "text": text,
    }
    log.info("Converted %ss of audio in %ss", media.duration, latency)
    await update.message.reply_text(text, reply_markup=feedback_buttons(result_id))


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    rating, _, result_id = (query.data or "").partition(":")
    item = _pending.pop(result_id, None)
    if item is None:
        await query.answer("Already rated. Dhonnobad!")
        return
    save_feedback(
        {
            "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "rating": rating,
            **item,
        }
    )
    await query.answer("Dhonnobad!")
    await query.edit_message_reply_markup(reply_markup=None)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Ami shudhu voice message bujhi. Mic button chepe dhore kotha bolun 🎤")


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set. Add it to your .env file.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_feedback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
