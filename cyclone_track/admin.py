from django.contrib import admin
from django.contrib import messages

from .models import CycloneTrack
from mailer.utils import SPCMailer


@admin.register(CycloneTrack)
class CycloneTrackAdmin(admin.ModelAdmin):
    list_display = (
        "cyclone_name",
        "issued_time",
        "issued_agency",
        "track_file",
        "geometry_computed",
        "country",
        "notify",
        "mail_configuration",
    )
    list_select_related = ("country",)
    readonly_fields = ("geometry",)
    search_fields = (
        "cyclone_name",
        "issued_agency",
        "track_file",
        "country__short_name",
        "country__long_name",
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Only send on initial create in admin.
        if change:
            return
        if not obj.notify:
            return
        if not obj.mail_configuration_id:
            self.message_user(
                request,
                "notify=true but no mail_configuration was selected; email not sent.",
                level=messages.ERROR,
            )
            return

        result = SPCMailer.send_with_config_sync(obj.mail_configuration)
        if not result.ok:
            self.message_user(
                request,
                f"Email send failed (Graph {result.status_code}): {result.response_text}",
                level=messages.ERROR,
            )
            return

        self.message_user(request, "Notification email sent.", level=messages.SUCCESS)
