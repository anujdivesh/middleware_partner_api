from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MailConfiguration, MailRecipient
from .serializers import (
    MailConfigurationSendSerializer,
    MailConfigurationSerializer,
    MailRecipientSerializer,
    SendEmailSerializer,
)
from .utils import SPCMailer


SendResultSerializer = inline_serializer(
    "SendResult",
    fields={
        "ok": serializers.BooleanField(),
        "error": serializers.CharField(required=False),
    },
)


class MailRecipientListCreateView(ListCreateAPIView):
    queryset = MailRecipient.objects.all().order_by("email")
    serializer_class = MailRecipientSerializer
    permission_classes = (IsAdminUser,)


class MailRecipientDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MailRecipient.objects.all()
    serializer_class = MailRecipientSerializer
    permission_classes = (IsAdminUser,)


class MailConfigurationListCreateView(ListCreateAPIView):
    queryset = MailConfiguration.objects.all().prefetch_related("recipients").order_by("name")
    serializer_class = MailConfigurationSerializer
    permission_classes = (IsAdminUser,)


class MailConfigurationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MailConfiguration.objects.all().prefetch_related("recipients")
    serializer_class = MailConfigurationSerializer
    permission_classes = (IsAdminUser,)


class MailConfigurationSendView(APIView):
    permission_classes = (IsAdminUser,)

    @extend_schema(
        summary="Send a mail configuration's email",
        description="Uses the configuration's subject/body/recipients unless overridden.",
        request=MailConfigurationSendSerializer,
        responses={200: SendResultSerializer, 502: SendResultSerializer},
    )
    def post(self, request, pk: int):
        config = get_object_or_404(MailConfiguration, pk=pk)
        serializer = MailConfigurationSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        result = SPCMailer.send_with_config_sync(
            config,
            subject=payload.get("subject"),
            body=payload.get("body"),
            to_emails=payload.get("to"),
        )

        if not result.ok:
            return Response({"ok": False, "error": result.error}, status=502)

        return Response({"ok": True})


class SendEmailView(APIView):
    """POST {"recipients": [...], "subject": "...", "message": "..."}"""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Send an email",
        description="Sends from GEM OPM <opm@spc.int> via SendGrid. `message` may be plain text or HTML.",
        request=SendEmailSerializer,
        responses={200: SendResultSerializer, 502: SendResultSerializer},
        examples=[
            OpenApiExample(
                "Request",
                value={"recipients": ["someone@spc.int"], "subject": "Test", "message": "Hello"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        result = SPCMailer.send_email(
            payload["recipients"],
            subject=payload["subject"],
            body=payload["message"],
        )

        if not result.ok:
            return Response({"ok": False, "error": result.error}, status=502)

        return Response({"ok": True, "recipients": payload["recipients"]})
