import requests

from django.conf import settings
from django.core.management import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    help = "Set new telegram webhook"

    def add_arguments(self, parser) -> None:
        parser.add_argument("root_url", type=str)

    def handle(self, *args, **options):
        root_url = options["root_url"]
        webhook_path = reverse("webhooks:telegram_webhook")
        webhook_url = f"{root_url}{webhook_path}"

        set_webhook_api = f"https://api.telegram.org/bot{settings.TELEGRAM_API_TOKEN}/setWebhook"

        self.stdout.write(f"Setting webhook url {webhook_url}\n")

        url = requests.post(set_webhook_api, data={"url": webhook_url})
