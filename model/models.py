from django.db import models as dj_models


class ModelDomain(dj_models.Model):
    name = dj_models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "model_domain"

    def __str__(self) -> str:
        return self.name


class ModelPriority(dj_models.Model):
    name = dj_models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "model_priority"

    def __str__(self) -> str:
        return self.name


class ModelStatus(dj_models.Model):
    name = dj_models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "model_status"
        verbose_name = "Model status"
        verbose_name_plural = "Model status"

    def __str__(self) -> str:
        return self.name


class Model(dj_models.Model):
    name = dj_models.CharField(max_length=255)
    location = dj_models.CharField(max_length=500, blank=True)
    server_name = dj_models.CharField(max_length=255, blank=True)
    inputs = dj_models.JSONField(null=True, blank=True)
    dry_run_command = dj_models.TextField(blank=True)

    class Meta:
        db_table = "model"

    def __str__(self) -> str:
        return self.name


class ModelRun(dj_models.Model):
    name = dj_models.CharField(max_length=255, blank=True)
    models = dj_models.ManyToManyField(
        Model,
        related_name="runs",
        blank=True,
    )
    model_domain = dj_models.ForeignKey(
        ModelDomain,
        on_delete=dj_models.PROTECT,
        related_name="runs",
        db_column="model_domain_id",
    )
    tc_track = dj_models.ForeignKey(
        "cyclone_track.CycloneTrack",
        on_delete=dj_models.PROTECT,
        related_name="model_runs",
        db_column="tc_track_id",
    )
    priority = dj_models.ForeignKey(
        ModelPriority,
        on_delete=dj_models.PROTECT,
        related_name="runs",
    )

    model_run_completed = dj_models.BooleanField(default=False)

    class Meta:
        db_table = "model_run"
        ordering = ("-id",)

    def __str__(self) -> str:
        label = self.name or f"Run {self.pk}"
        return label


class ModelLogs(dj_models.Model):
    model_run = dj_models.ForeignKey(
        ModelRun,
        on_delete=dj_models.CASCADE,
        related_name="logs",
        db_column="model_run_id",
    )
    status = dj_models.ForeignKey(
        ModelStatus,
        null=True,
        blank=True,
        on_delete=dj_models.PROTECT,
        related_name="log_entries",
    )
    logs = dj_models.TextField()

    class Meta:
        db_table = "model_logs"
        verbose_name = "Model log"
        verbose_name_plural = "Model logs"

    def __str__(self) -> str:
        return f"Logs for run {self.model_run_id}"
