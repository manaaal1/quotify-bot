# bot.py
import os
import logging
import random
from datetime import time
import requests
import pytz
import asyncio
from threading import Thread

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUOTES_API = "https://zenquotes.io/api/random"
FALLBACK_QUOTES = [
    "The best way to predict the future is to invent it. — Alan Kay",
    "Be yourself; everyone else is already taken. — Oscar Wilde",
    "Do small things with great love. — Mother Teresa",
    "The only limit is your mind. — Unknown",
]

# Pick a random quote (API or fallback)
def get_random_quote():
    try:
        r = requests.get(QUOTES_API, timeout=6)
        r.raise_for_status()
        data = r.json()
        q = data[0]
        return f'"{q.get("q")}" — {q.get("a") or "Unknown"}'
    except Exception:
        return random.choice(FALLBACK_QUOTES)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Quotify! I post a daily quote to your channel. "
        "If you are the owner, use /post <message> to post now."
    )

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only: post a message immediately to the channel."""
    admin_id = os.getenv("ADMIN_ID")
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

    text = get_random_quote()
    await context.bot.send_message(chat_id=channel, text=text)


# --- Flask setup to satisfy Render's port scan ---
flask_app = Flask("Quotify")

@flask_app.route("/")
def home():
    return "Quotify Bot is running!"


def run_flask():
    PORT = int(os.getenv("PORT", 8443))
    flask_app.run(host="0.0.0.0", port=PORT)


# --- Main bot code ---
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Missing BOT_TOKEN environment variable.")
        return

    # Start Flask in a separate thread so it doesn't block the bot
    Thread(target=run_flask, daemon=True).start()

    # Create bot and clear any existing webhook
    bot = Bot(token=TOKEN)
    asyncio.run(bot.delete_webhook(drop_pending_updates=True))

    # Build Telegram app
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))

    # Clear any leftover jobs
    for job in list(app.job_queue.jobs()):
        job.schedule_removal()

    # Schedule daily quote
    tz_name = os.getenv("TZ", "Africa/Addis_Ababa")
    tz = pytz.timezone(tz_name)
    hour = int(os.getenv("DAILY_HOUR", "11"))
    minute = int(os.getenv("DAILY_MIN", "11"))
    job = app.job_queue.run_daily(send_daily, time(hour, minute, tzinfo=tz))
    logger.info(f"Next quote scheduled for: {job.next_t_run}")

    logger.info("Starting in polling mode (Render compatible).")
    app.run_polling()  # keeps running in the background


if __name__ == "__main__":
    main()
