from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "event_type",
            "country",
            "cyclone_track",
            "hazards",
            "risks",
            "citizen_sciences",
            "model_run",
        )
        read_only_fields = ("id",)
