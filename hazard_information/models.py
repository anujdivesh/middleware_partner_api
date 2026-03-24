from django.db import models

from country.models import Country
from event_type.models import EventType
from hazard_type.models import HazardType


class HazardInformation(models.Model):

    title = models.CharField(max_length=255, null=True, blank=True)
    protocol = models.CharField(max_length=50)
    url = models.URLField(max_length=2000)


    created_at = models.DateTimeField(auto_now_add=True)

    hazard_type = models.ForeignKey(
        HazardType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hazard_information",
    )

    event_type = models.ForeignKey(
        EventType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hazard_information",
    )

    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)

    layer_name = models.CharField(max_length=255, null=True, blank=True)
    style = models.CharField(max_length=255, null=True, blank=True)

    country = models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hazard_information",
    )

    model_run = models.ForeignKey(
        "model.ModelRun",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hazard_information",
    )

    class Meta:
        db_table = "hazard_information"

    def __str__(self) -> str:
        parts: list[str] = []
        if self.title:
            parts.append(self.title)
        if self.country_id and self.country:
            parts.append(self.country.short_name or self.country.long_name)
        if self.event_type_id and self.event_type:
            parts.append(self.event_type.event_name)
        if self.layer_name:
            parts.append(self.layer_name)
        parts.append(self.protocol)
        prefix = " | ".join(parts)
        return f"{prefix}: {self.url}"
