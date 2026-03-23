from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import APIException
from django.db import transaction

from .models import CycloneTrack
from .serializers import CycloneTrackSerializer
from mailer.utils import SPCMailer


class CycloneTrackListCreateView(ListCreateAPIView):
    queryset = CycloneTrack.objects.all().order_by("-id")
    serializer_class = CycloneTrackSerializer

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # Needed for file upload
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        with transaction.atomic():
            instance: CycloneTrack = serializer.save()

            if not instance.notify:
                return

            if not instance.mail_configuration_id:
                raise APIException("mail_configuration is required when notify=true")

            result = SPCMailer.send_with_config_sync(instance.mail_configuration)
            if not result.ok:
                raise APIException(
                    f"Email send failed (Graph {result.status_code}): {result.response_text}"
                )


class CycloneTrackRetrieveView(RetrieveAPIView):
    queryset = CycloneTrack.objects.all()
    serializer_class = CycloneTrackSerializer

    # GET is public (same as list)
    permission_classes = (IsAuthenticatedOrReadOnly,)
