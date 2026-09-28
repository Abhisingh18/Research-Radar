"""Sends messages via the Telegram Bot API.

Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (talk to @BotFather to create a
bot, then message it once and hit
https://api.telegram.org/bot<token>/getUpdates to find your chat id).

If either env var is missing, `send` becomes a no-op that returns False so
the pipeline can keep running in a "dry run" mode (e.g. for local testing).
"""

from __future__ import annotations

import os

import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def is_configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN")) and bool(os.environ.get("TELEGRAM_CHAT_ID"))


def send(text: str, timeout: float = 15.0) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False

    url = TELEGRAM_API_URL.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return True
