import requests

import anthropic

from celery import shared_task

from django.conf import settings


@shared_task
def send_telegram_reply(message):
    name = message["message"]["from"]["first_name"]
    text = message["message"]["text"]
    chat_id = message["message"]["chat"]["id"]

    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=settings.ANTHROPIC_API_KEY
    )

    message = client.messages.create(
        model="claude-2.0",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": text}]
    )

    reply_url = f"https://api.telegram.org/bot{settings.TELEGRAM_API_TOKEN}/sendMessage"

    data = {"chat_id": chat_id, "text": message.content[0].text}
    print(message.content)
    print(type(message.content))
    requests.post(reply_url, data=data)
