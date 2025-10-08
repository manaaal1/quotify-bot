Quotify — Daily Quotes Channel Bot
---------------------------------
A small Python Telegram bot that auto-posts a curated quote to a private channel every day, and allows the owner to post on-demand.

Tech: Python, python-telegram-bot, requests, apscheduler/job-queue
Deployment: Deployable to Render free web services (webhook mode).

Features:
- /start — welcome
- /post <message> — post immediately (admin only)
- Daily automatic quote (configurable hour & TZ)

Notes: Bot token and channel id are stored as environment variables. See bot.py and deploy instructions.
