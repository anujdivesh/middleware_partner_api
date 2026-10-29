from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.exceptions import ValidationError


def parse_date_param(name, value, end_of_day=False):
    """Accept YYYY-MM-DD or an ISO 8601 datetime; naive values use the server timezone."""
    parsed = parse_datetime(value)
    if parsed is None:
        day = parse_date(value)
        if day is None:
            raise ValidationError({name: "Use YYYY-MM-DD or an ISO 8601 datetime."})
        parsed = datetime.combine(day, time.max if end_of_day else time.min)
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


def filter_date_range(queryset, params, field):
    """Apply ?start_date= / ?end_date= (both inclusive) to a datetime field."""
    start_date = params.get("start_date")
    if start_date:
        queryset = queryset.filter(
            **{f"{field}__gte": parse_date_param("start_date", start_date)}
        )

    end_date = params.get("end_date")
    if end_date:
        queryset = queryset.filter(
            **{f"{field}__lte": parse_date_param("end_date", end_date, end_of_day=True)}
        )

    return queryset
