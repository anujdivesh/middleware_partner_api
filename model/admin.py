from django.contrib import admin

from .models import Model, ModelDomain, ModelLogs, ModelPriority, ModelRun, ModelStatus


@admin.register(ModelDomain)
class ModelDomainAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ModelPriority)
class ModelPriorityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ModelStatus)
class ModelStatusAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name", "server_name", "location")
    search_fields = ("name", "server_name", "location")


@admin.register(ModelRun)
class ModelRunAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "model_run_time", "model_domain", "tc_track", "priority")
    search_fields = ("name", "models__name")
    list_select_related = ("model_domain", "tc_track", "priority")
    filter_horizontal = ("models", "hazards", "risks")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Option labels include the related country/category; fetch them in one query.
        if db_field.name == "hazards":
            kwargs["queryset"] = db_field.related_model.objects.select_related("country")
        elif db_field.name == "risks":
            kwargs["queryset"] = db_field.related_model.objects.select_related(
                "risk_category", "country"
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(ModelLogs)
class ModelLogsAdmin(admin.ModelAdmin):
    list_display = ("id", "model_run", "status")
    search_fields = ("model_run__name", "model_run__id")
    list_select_related = ("model_run", "status")

