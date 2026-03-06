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
            "geometry_computed",
            "country",
        )
        read_only_fields = ("id", "geometry", "geometry_computed")
