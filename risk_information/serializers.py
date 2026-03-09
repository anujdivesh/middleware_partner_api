from rest_framework import serializers

from .models import RiskInformation


class RiskInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskInformation
        fields = (
            "id",
            "title",
            "risk_category",
            "upload",
            "geometry",
            "geometry_computed",
            "created_at",
            "country",
            "event_type",
        )
        read_only_fields = (
            "id",
            "geometry",
            "geometry_computed",
            "created_at",
        )
