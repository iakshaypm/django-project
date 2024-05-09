from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
webhook_secret = settings.STRIPE_WEBHOOK_SECRET


class CreateCheckoutSession(APIView):
    def post(self, request):
        dataDict = dict(request.data)
        price = dataDict['price'][0]
        product_name = dataDict['product_name'][0]
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': product_name,
                    },
                    'unit_amount': int(price)*100
                },
                'quantity': 1
            }],
            mode='payment',
            success_url='https://www.google.com',
            cancel_url='https://www.facebook.com'
        )
        # return redirect(checkout_session.url, code=303)
        return Response({
            'status': status.HTTP_200_OK,
            'message': 'Mark has been added',
            'data': {}
        })


class WebHook(APIView):
    def post(self, request):
        event = None
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as err:
            # Invalid payload
            raise err
        except stripe.error.SignatureVerificationError as err:
            # Invalid signature
            raise err

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            print("--------payment_intent ---------->", payment_intent)
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object
            print("--------payment_method ---------->", payment_method)
        # ... handle other event types
        else:
            print('Unhandled event type {}'.format(event.type))

        return JsonResponse(success=True, safe=False)
