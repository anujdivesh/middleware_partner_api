from django.contrib import admin

from .models import RiskInformation


@admin.register(RiskInformation)
class RiskInformationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "risk_category",
        "upload",
        "geometry_computed",
        "created_at",
        "country",
        "event_type",
        "model_run",
    )
    list_select_related = ("risk_category", "country", "event_type", "model_run")
    search_fields = (
        "title",
        "risk_category__short_name",
        "risk_category__long_name",
        "event_type__event_name",
        "country__short_name",
        "country__long_name",
        "model_run__name",
        "upload",
    )

