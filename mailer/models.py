from django.db import models


class MailRecipient(models.Model):
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email


class MailConfiguration(models.Model):
    """Message template + recipients. Transport/sender come from settings.EMAIL_*."""

    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)

    subject = models.CharField(max_length=255)
    body = models.TextField(help_text="HTML body")

    recipients = models.ManyToManyField(MailRecipient, blank=True, related_name="mail_configurations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
