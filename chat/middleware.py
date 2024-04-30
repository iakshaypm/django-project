from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.authentication import JWTAuthentication

from channels.middleware import BaseMiddleware


class TokenAuthMiddleware(BaseMiddleware):
    jwt_object = JWTAuthentication()

    def __init__(self, inner):
        super().__init__(inner)

    def __call__(self, scope, receive, send):

        try:
            headers = dict(scope['headers'])
            raw_token = headers[b'token']
            validated_token = self.jwt_object.get_validated_token(raw_token)
            user = self.jwt_object.get_user(validated_token)
        except ValueError:
            user = AnonymousUser()
        scope['user'] = user
        return super().__call__(scope, receive, send)
