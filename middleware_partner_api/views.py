from django.http import JsonResponse
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from .authentication import token_expires_at, token_is_expired

def root(request):
    return redirect("/partner_api/")

def partner_api_root(request):
    return JsonResponse({"message": "Welcome to Pacific Disaster api"})


class ObtainExpiringAuthToken(ObtainAuthToken):
    """Returns the user's token, replacing it first if it has expired."""

    @extend_schema(
        tags=["auth"],
        summary="Get an API token",
        description=(
            "Exchange a username and password for a token. Tokens expire 2 days after "
            "they are issued; calling this again before then returns the same token."
        ),
        auth=[],
        responses=inline_serializer(
            "AuthTokenResponse",
            fields={"token": serializers.CharField(), "expires_at": serializers.DateTimeField()},
        ),
        examples=[
            OpenApiExample(
                "Response",
                value={"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b", "expires_at": "2026-10-23T00:15:21Z"},
                response_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(user=user)
        if not created and token_is_expired(token):
            token.delete()
            token = Token.objects.create(user=user)

        return Response({"token": token.key, "expires_at": token_expires_at(token)})
