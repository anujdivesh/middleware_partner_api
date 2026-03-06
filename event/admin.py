from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "country", "cyclone_track")
    list_select_related = ("event_type", "country", "cyclone_track")
    autocomplete_fields = (
        "event_type",
        "country",
        "cyclone_track",
        "hazards",
        "risks",
        "citizen_sciences",
    )
