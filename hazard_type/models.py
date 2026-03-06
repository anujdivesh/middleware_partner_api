from django.db import models


class HazardType(models.Model):
    hazard_type = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.hazard_type
