from django.db import models


class Project(models.Model):
    project_code = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.project_code} - {self.project_name}"
