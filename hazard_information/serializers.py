from rest_framework import serializers

from .models import HazardInformation


class HazardInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HazardInformation
        fields = (
            "id",
            "protocol",
            "url",
            "hazard_type",
            "event_type",
            "min",
            "max",
            "layer_name",
            "style",
            "country",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
