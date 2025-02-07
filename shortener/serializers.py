from rest_framework import serializers
from .models import Shortener


class ShortenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shortener
        fields = "__all__"


class ShortenerSerializerCreator(serializers.Serializer):
    long_url = serializers.URLField(required=True)

    def create(self, validated_data):
        return Shortener.objects.create(long_url=validated_data["long_url"])

    def update(self, instance: Shortener, validated_data: dict):
        instance.long_url = validated_data.get("long_url", instance.long_url)
        return instance
