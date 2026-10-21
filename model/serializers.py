from rest_framework import serializers
from .models import Model, ModelRun, ModelLogs

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class ModelRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelRun
        fields = '__all__'

class ModelLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelLogs
        fields = '__all__'
