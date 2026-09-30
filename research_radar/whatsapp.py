"""Sends WhatsApp messages via CallMeBot (https://www.callmebot.com/blog/free-api-whatsapp-messages/).

CallMeBot is a free, unofficial personal-use WhatsApp API - no business
account, no billing, no template approval. Good fit for a handful of
personal alerts a day; not meant for high-volume or commercial use.

Setup (one-time, from your own phone):
  1. Save +34 644 71 71 92 as a contact.
  2. WhatsApp it: "I allow callmebot to send me messages"
  3. It replies with your API key.

Set:
  CALLMEBOT_PHONE   your number with country code, digits only, e.g. "919648531091"
  CALLMEBOT_APIKEY  the key CallMeBot sent you

Keep both out of source control - local env var or GitHub Actions secret only.

If either var is missing, `send` is a no-op that returns False, same as the
Telegram module, so the pipeline degrades gracefully.
"""

from __future__ import annotations

import os

import requests

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def is_configured() -> bool:
    return bool(os.environ.get("CALLMEBOT_PHONE")) and bool(os.environ.get("CALLMEBOT_APIKEY"))


def send(text: str, timeout: float = 15.0) -> bool:
    phone = os.environ.get("CALLMEBOT_PHONE")
    apikey = os.environ.get("CALLMEBOT_APIKEY")
    if not phone or not apikey:
        return False

    response = requests.get(
        CALLMEBOT_URL,
        params={"phone": phone, "text": text, "apikey": apikey},
        timeout=timeout,
    )
    response.raise_for_status()
    return "queued" in response.text.lower()
