from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from .models import MailConfiguration


@dataclass(frozen=True)
class SendResult:
    ok: bool
    error: str = ""


class SPCMailer:
    @staticmethod
    def get_default_configuration() -> MailConfiguration:
        name = getattr(settings, "MAILER_DEFAULT_CONFIGURATION_NAME", None)
        queryset = MailConfiguration.objects.filter(is_active=True)
        if name:
            try:
                return queryset.get(name=name)
            except MailConfiguration.DoesNotExist as exc:
                raise RuntimeError(
                    f"No active MailConfiguration found with name={name!r}"
                ) from exc

        configs = list(queryset.order_by("id")[:2])
        if len(configs) == 1:
            return configs[0]
        if len(configs) == 0:
            raise RuntimeError("No active MailConfiguration exists")
        raise RuntimeError(
            "Multiple active MailConfigurations exist; set MAILER_DEFAULT_CONFIGURATION_NAME"
        )

    @staticmethod
    def send_notification_email_sync(to: str, subject: str, body: str) -> bool:
        config = SPCMailer.get_default_configuration()
        to_emails = [email.strip() for email in (to or "").split(",") if email.strip()]
        result = SPCMailer.send_with_config_sync(
            config, subject=subject, body=body, to_emails=to_emails
        )
        if not result.ok:
            raise RuntimeError(result.error)
        return True

    @staticmethod
    def send_with_config_sync(
        config: MailConfiguration,
        *,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        to_emails: Optional[Iterable[str]] = None,
    ) -> SendResult:
        if not config.is_active:
            raise ValueError("Mail configuration is inactive")

        subject = subject or config.subject
        body = body or config.body
        if not subject or not body:
            raise ValueError("Email subject/body cannot be empty")

        if to_emails is None:
            to_emails = list(
                config.recipients.filter(is_active=True).values_list("email", flat=True)
            )
        return SPCMailer.send_email(to_emails, subject=subject, body=body)

    @staticmethod
    def send_email(to_emails: Iterable[str], *, subject: str, body: str) -> SendResult:
        """Send one email over SMTP (settings.EMAIL_*, SendGrid).

        `body` may be HTML or plain text; HTML gets a plain-text alternative.
        """
        to_emails = [email.strip() for email in to_emails if str(email).strip()]
        if not to_emails:
            raise ValueError("No recipients specified")

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            return SendResult(
                ok=False,
                error="SMTP credentials missing: set SENDGRID_SMTP_USERNAME and SENDGRID_SMTP_PASSWORD",
            )

        plain_body = strip_tags(body)
        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
            reply_to=settings.EMAIL_REPLY_TO,
        )
        if plain_body != body:
            message.attach_alternative(body, "text/html")
        try:
            message.send(fail_silently=False)
        except Exception as exc:
            return SendResult(ok=False, error=f"{type(exc).__name__}: {exc}")
        return SendResult(ok=True)
