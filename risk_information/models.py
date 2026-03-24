import os

from django.core.validators import FileExtensionValidator
from django.db import models

from event_type.models import EventType
from risk_category.models import RiskCategory

from .utils import convert_uploaded_file_to_geometry


class RiskInformation(models.Model):

    title = models.CharField(max_length=255, null=True, blank=True)
    risk_category = models.ForeignKey(
        RiskCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="risk_information",
    )


    upload = models.FileField(
        upload_to="risk_information/",
        validators=[FileExtensionValidator(allowed_extensions=["geojson", "csv", "gpkg"])],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    geometry = models.JSONField(null=True, blank=True)

    geometry_computed = models.BooleanField(default=False)

    country = models.ForeignKey(
        'country.Country',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='risk_information',
    )

    event_type = models.ForeignKey(
        EventType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='risk_information',
    )

    model_run = models.ForeignKey(
        "model.ModelRun",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="risk_information",
    )

    class Meta:
        db_table = "risk_information"

    def __str__(self) -> str:
        parts: list[str] = [f"RiskInformation {self.pk}"]

        if self.title:
            parts.append(self.title)

        if self.risk_category_id and self.risk_category:
            parts.append(str(self.risk_category))
        if self.country_id and self.country:
            parts.append(self.country.short_name or self.country.long_name)
        if self.event_type_id and self.event_type:
            parts.append(self.event_type.event_name)
        if self.upload:
            parts.append(os.path.basename(self.upload.name))

        return " | ".join(parts)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_upload_name = None
        if not is_new:
            old_upload_name = (
                RiskInformation.objects.filter(pk=self.pk)
                .values_list("upload", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        upload_changed = (
            self.upload
            and old_upload_name is not None
            and str(old_upload_name) != str(self.upload.name)
        )

        should_generate = bool(self.upload) and (self.geometry is None or is_new or upload_changed)
        if not should_generate:
            return

        try:
            with self.upload.open("rb") as file_obj:
                file_path = None
                try:
                    file_path = self.upload.path
                except Exception:
                    file_path = None
                geometry = convert_uploaded_file_to_geometry(
                    file_obj=file_obj,
                    filename=self.upload.name,
                    file_path=file_path,
                )
        except Exception:
            RiskInformation.objects.filter(pk=self.pk).update(geometry_computed=False)
            return

        def is_blank_geometry(value) -> bool:
            if value is None:
                return True
            if isinstance(value, list):
                return len(value) == 0
            if isinstance(value, dict):
                if len(value) == 0:
                    return True
                features = value.get("features")
                if isinstance(features, list) and len(features) == 0:
                    return True
            return False

        if is_blank_geometry(geometry):
            RiskInformation.objects.filter(pk=self.pk).update(
                geometry=None,
                geometry_computed=False,
            )
            return

        RiskInformation.objects.filter(pk=self.pk).update(
            geometry=geometry,
            geometry_computed=True,
        )
