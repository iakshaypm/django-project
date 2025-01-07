from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from chat.tasks import send_telegram_reply


class TelegramWebhook(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """Handle POST requests to send a reply via Telegram.

        This method processes incoming POST requests and triggers an
        asynchronous task to send a reply using the provided data. It currently
        does not validate the request token for authorization, which may be
        necessary for security purposes.

        Args:
            request (Request): The HTTP request object containing the data to be sent.

        Returns:
            Response: A response indicating the success of the operation.
        """

        # if token != settings.TELEGRAM_WEBHOOK_TOKEN:
        #     return Response(
        #         {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
        #     )

        # print(request.data)
        send_telegram_reply.delay(request.data)
        return Response({"success": True})
