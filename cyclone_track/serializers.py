from rest_framework import serializers

from .models import CycloneTrack


class CycloneTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycloneTrack
        fields = (
            "id",
            "cyclone_name",
            "issued_time",
            "issued_agency",
            "track_file",
            "geometry",
        )
        read_only_fields = ("id", "geometry")
