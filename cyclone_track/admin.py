from django.contrib import admin

from .models import CycloneTrack


@admin.register(CycloneTrack)
class CycloneTrackAdmin(admin.ModelAdmin):
    list_display = ("cyclone_name", "issued_time", "issued_agency", "track_file")
    readonly_fields = ("geometry",)
