# bot.py
import os
import logging
import random
from datetime import time
import requests
import pytz

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUOTES_API = "https://type.fit/api/quotes"
FALLBACK_QUOTES = [
    "The best way to predict the future is to invent it. — Alan Kay",
    "Be yourself; everyone else is already taken. — Oscar Wilde",
    "Do small things with great love. — Mother Teresa",
    "The only limit is your mind. — Unknown",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Quotify! I post a daily quote to your channel. "
        "If you are the owner, use /post <message> to post now."
    )

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only: post a message immediately to the channel."""
    admin_id = os.getenv("ADMIN_ID")  # set to your Telegram user id (string)
    sender = update.effective_user
    if admin_id and str(sender.id) != admin_id:
        await update.message.reply_text("❌ You are not authorized to use /post.")
        return

    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /post <message>")
        return

    channel = os.getenv("CHANNEL_ID")
    if not channel:
        await update.message.reply_text("Server not configured: CHANNEL_ID missing.")
        return

    await context.bot.send_message(chat_id=channel, text=text)
    await update.message.reply_text("✅ Posted to channel.")

async def send_daily(context: ContextTypes.DEFAULT_TYPE):
    """Job: pick a quote (API or fallback) and post to channel."""
    channel = os.getenv("CHANNEL_ID")
    if not channel:
        logger.warning("CHANNEL_ID not set; skipping daily post.")
        return

    try:
        r = requests.get(QUOTES_API, timeout=6)
        r.raise_for_status()
        quotes = r.json()
        q = random.choice(quotes)
        text = f'"{q.get("text")}" — {q.get("author") or "Unknown"}'
    except Exception as e:
        logger.exception("Failed to fetch quotes; using fallback.")
        text = random.choice(FALLBACK_QUOTES)

    await context.bot.send_message(chat_id=channel, text=text)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Missing BOT_TOKEN environment variable.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))

    # Schedule daily job (default 09:00 Addis Ababa). Use env vars to override.
    tz_name = os.getenv("TZ", "Africa/Addis_Ababa")
    tz = pytz.timezone(tz_name)
    hour = int(os.getenv("DAILY_HOUR", "11"))
    minute = int(os.getenv("DAILY_MIN", "11"))
    app.job_queue.run_daily(send_daily, time(hour, minute, tzinfo=tz))

    # If WEBHOOK_URL env var is set, run webhook mode (recommended for hosting).
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://yourservice.onrender.com/<BOT_TOKEN>
    PORT = int(os.getenv("PORT", "8443"))

    if WEBHOOK_URL:
        # NOTE: python-telegram-bot provides run_webhook; hosting docs differ slightly by version.
        # This will start a small webserver to receive updates from Telegram.
        logger.info("Starting in webhook mode.")
        # webhook path should match the URL you give Telegram (we use token as path part)
        url_path = f"/{TOKEN}"
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=url_path, webhook_url=WEBHOOK_URL.rstrip("/"))
    else:
        logger.info("Starting in polling mode (local testing).")
        app.run_polling()

if __name__ == "__main__":
    main()