Quotify — Daily Quotes Channel Bot

A Python Telegram bot that automatically posts a daily inspirational quote to your channel, fetches quotes from an API with fallback options, and allows you to post messages on-demand.

Tech: Python, python-telegram-bot, requests, apscheduler/job-queue
Deployment: Deployable to Render free web services (polling or webhook mode).

Features:

/start — welcome message

/post — post immediately (admin only)

Daily automatic quote (configurable hour & timezone)

Notes: Bot token, channel ID, and admin ID are stored as environment variables. See bot.py and deployment instructions.
