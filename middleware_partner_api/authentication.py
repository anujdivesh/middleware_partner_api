"""DRF token auth where tokens expire after settings.API_TOKEN_LIFETIME."""

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


def token_expires_at(token: Token):
    return token.created + settings.API_TOKEN_LIFETIME


def token_is_expired(token: Token) -> bool:
    return timezone.now() >= token_expires_at(token)


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token_is_expired(token):
            token.delete()
            raise exceptions.AuthenticationFailed(
                "Token has expired. Request a new one from /partner_api/api-token-auth/."
            )
        return user, token
