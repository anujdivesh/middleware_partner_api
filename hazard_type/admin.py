from django.contrib import admin

from .models import HazardType


@admin.register(HazardType)
class HazardTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "hazard_type")
    search_fields = ("hazard_type",)
