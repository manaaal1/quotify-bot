Quotify — Daily Quotes Channel Bot

A Python Telegram bot that automatically posts a daily inspirational quote to your channel, fetches quotes from an API with fallback options, and allows you to post messages on-demand. Supports optional schedule persistence with PostgreSQL.

Tech: Python, python-telegram-bot, requests, apscheduler/job-queue
Deployment: Deployable to Render free web services (polling or webhook mode).

Features:

/start — welcome message

/post — post immediately (admin only)

Daily automatic quote (configurable hour & timezone)

Optional database persistence for scheduled posts

Notes: Bot token, channel ID, admin ID, and optional database URL are stored as environment variables. See bot.py and deployment instructions.
