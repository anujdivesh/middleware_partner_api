from rest_framework import serializers

from .models import EventType


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ("id", "event_name")
