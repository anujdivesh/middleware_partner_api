from django.db import models

from .utils import cyclone_csv_to_geojson


class CycloneTrack(models.Model):
    cyclone_name = models.CharField(max_length=255, null=True, blank=True)
    issued_time = models.DateTimeField(null=True, blank=True)
    issued_agency = models.CharField(max_length=255, null=True, blank=True)

    # Only mandatory field
    track_file = models.FileField(upload_to="cyclone_tracks/")

    geometry = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return self.cyclone_name or f"CycloneTrack {self.pk}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_track_name = None
        if not is_new:
            old_track_name = (
                CycloneTrack.objects.filter(pk=self.pk)
                .values_list("track_file", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        file_changed = (
            self.track_file
            and old_track_name is not None
            and str(old_track_name) != str(self.track_file.name)
        )

        should_generate = bool(self.track_file) and (self.geometry is None or is_new or file_changed)
        if not should_generate:
            return

        try:
            with self.track_file.open("rb") as file_obj:
                geojson = cyclone_csv_to_geojson(file_obj)
        except Exception:
            return

        if not geojson:
            return

        # If cyclone_name not provided, infer from CSV metadata.
        cyclone_name = self.cyclone_name
        try:
            cyclone_name = cyclone_name or geojson.get("metadata", {}).get("CycloneName")
        except Exception:
            pass

        CycloneTrack.objects.filter(pk=self.pk).update(
            geometry=geojson,
            cyclone_name=cyclone_name,
        )
