from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "event_datetime",
            "event_type",
            "country",
            "citizen_sciences",
            "model_runs",
        )
        read_only_fields = ("id",)
