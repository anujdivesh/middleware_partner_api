from django.contrib import admin

from .models import HazardInformation


@admin.register(HazardInformation)
class HazardInformationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "protocol",
        "url",
        "hazard_type",
        "event_type",
        "country",
        "layer_name",
        "min",
        "max",
        "created_at",
    )
    list_select_related = ("country", "hazard_type", "event_type")
    search_fields = (
        "protocol",
        "url",
        "layer_name",
        "hazard_type__hazard_type",
        "event_type__event_name",
        "country__short_name",
        "country__long_name",
    )
