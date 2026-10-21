from django.contrib import admin

from .models import MailConfiguration, MailRecipient


@admin.register(MailRecipient)
class MailRecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_active", "created_at")
    search_fields = ("email", "name")
    #list_filter = ("is_active",)


@admin.register(MailConfiguration)
class MailConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "subject", "updated_at")
    search_fields = ("name", "subject")
    #list_filter = ("is_active",)
    filter_horizontal = ("recipients",)
