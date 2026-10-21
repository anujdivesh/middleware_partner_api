from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "event_datetime",
        "event_type",
        "country",
    )
    list_select_related = ("event_type", "country")
    autocomplete_fields = (
        "event_type",
        "country",
        "citizen_sciences",
        "model_runs",
    )
