from rest_framework import serializers
from .models import Country

from island.models import Island


class IslandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Island
        fields = ("id", "island_name")

class CountrySerializer(serializers.ModelSerializer):
    islands = IslandSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = '__all__'
