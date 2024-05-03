from rest_framework import serializers
from .models import Detection

class PredictionSerializer(serializers.Serializer):
    input_data = serializers.ListField(child=serializers.FloatField())

class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = ["id", "title", "content", "published_date"]