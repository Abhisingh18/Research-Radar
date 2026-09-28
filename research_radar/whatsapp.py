"""Sends messages via Twilio's WhatsApp API.

Requires a Twilio account with WhatsApp enabled (the free sandbox works for
personal use — see https://www.twilio.com/docs/whatsapp/sandbox).

Set:
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_WHATSAPP_FROM   e.g. "whatsapp:+14155238886" (Twilio sandbox number)
  TWILIO_WHATSAPP_TO     e.g. "whatsapp:+91XXXXXXXXXX" (your number, with country code)

Keep the phone number out of source control — set it as a local env var or a
GitHub Actions secret, never commit it.

If any var is missing, `send` is a no-op that returns False, same as the
Telegram module, so the pipeline degrades gracefully.
"""

from __future__ import annotations

import os

import requests

TWILIO_URL = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"


def is_configured() -> bool:
    return all(
        os.environ.get(var)
        for var in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "TWILIO_WHATSAPP_TO")
    )


def send(text: str, timeout: float = 15.0) -> bool:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_WHATSAPP_FROM")
    to_number = os.environ.get("TWILIO_WHATSAPP_TO")
    if not all((sid, token, from_number, to_number)):
        return False

    url = TWILIO_URL.format(sid=sid)
    response = requests.post(
        url,
        auth=(sid, token),
        data={"From": from_number, "To": to_number, "Body": text},
        timeout=timeout,
    )
    response.raise_for_status()
    return True
