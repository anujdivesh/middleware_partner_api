from django.contrib import admin

from .models import CycloneTrack


@admin.register(CycloneTrack)
class CycloneTrackAdmin(admin.ModelAdmin):
    list_display = (
        "cyclone_name",
        "issued_time",
        "issued_agency",
        "track_file",
        "geometry_computed",
        "country",
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
