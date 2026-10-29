from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import APIException, NotFound, ValidationError
from django.db import transaction
from django.db.models import F
import logging

from middleware_partner_api.filters import filter_date_range
from .models import CycloneTrack
from .serializers import CycloneTrackSerializer
from mailer.utils import SPCMailer


logger = logging.getLogger(__name__)


def filtered_tracks(params):
    """Tracks newest issued first, filtered by ?cyclone_track_type=, ?country=,
    ?start_date= and ?end_date= (on issued_time)."""
    queryset = CycloneTrack.objects.all().order_by(
        F("issued_time").desc(nulls_last=True), "-id"
    )

    for param in ("cyclone_track_type", "country"):
        value = params.get(param)
        if value:
            if not value.isdigit():
                raise ValidationError({param: "Must be an integer id."})
            queryset = queryset.filter(**{f"{param}_id": int(value)})

    return filter_date_range(queryset, params, "issued_time")


class CycloneTrackListCreateView(ListCreateAPIView):
    serializer_class = CycloneTrackSerializer

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # Needed for file upload
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return filtered_tracks(self.request.query_params)

    def perform_create(self, serializer):
        with transaction.atomic():
            instance: CycloneTrack = serializer.save()

            if instance.notify and not instance.mail_configuration_id:
                # This should already be enforced by serializer validation, but keep it here
                # as a defensive guard.
                raise APIException("mail_configuration is required when notify=true")

            def _send_notification_best_effort(track_id: int) -> None:
                try:
                    track = CycloneTrack.objects.select_related("mail_configuration").get(
                        pk=track_id
                    )
                    if not track.notify:
                        return
                    if not track.mail_configuration_id:
                        logger.warning(
                            "CycloneTrack notify=true but mail_configuration is missing; skipping email. track_id=%s",
                            track_id,
                        )
                        return

                    result = SPCMailer.send_with_config_sync(track.mail_configuration)
                    if not result.ok:
                        logger.error(
                            "CycloneTrack email send failed; continuing without failing request. track_id=%s error=%s",
                            track_id,
                            result.error[:2000],
                        )
                except Exception:
                    # Never let email/SMTP issues break cyclone track ingestion.
                    logger.exception(
                        "CycloneTrack email send raised exception; continuing without failing request. track_id=%s",
                        track_id,
                    )

            # Attempt email only after the DB commit succeeds.
            transaction.on_commit(lambda: _send_notification_best_effort(instance.pk))


class CycloneTrackRetrieveView(RetrieveAPIView):
    queryset = CycloneTrack.objects.all()
    serializer_class = CycloneTrackSerializer

    # GET is public (same as list)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class CycloneTrackLatestView(RetrieveAPIView):
    """The most recently issued track; accepts the same filters as the list."""

    serializer_class = CycloneTrackSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        track = filtered_tracks(self.request.query_params).first()
        if track is None:
            raise NotFound("No cyclone track found.")
        return track
