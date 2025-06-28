from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import PasswordProtectedShortener, PrivateShortener, Shortener


class ShortenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shortener
        fields = ["short_url", "long_url", "created", "updated", "times_followed", "access_token", "user", "expires_at", "is_active"]
        read_only_fields = [
            "short_url",
            "created",
            "updated",
            "times_followed",
            "access_token",
            "password",
            "user",
            "is_active",
        ]


class ShortenerSerializerCreator(serializers.Serializer):
    long_url = serializers.URLField(required=True)
    is_private = serializers.BooleanField(default=False)
    has_password = serializers.BooleanField(default=False)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def create(self, validated_data: dict):
        long_url = validated_data["long_url"]
        is_private = validated_data.get("is_private", False)
        has_password = validated_data.get("has_password", False)
        password = validated_data.get("password")
        expires_at = validated_data.get("expires_at")
        user = self.context['request'].user if 'request' in self.context and self.context['request'].user.is_authenticated else None

        if is_private:
            shortener = PrivateShortener.objects.create(long_url=long_url, user=user, expires_at=expires_at)
        elif has_password and password:
            shortener = PasswordProtectedShortener.objects.create(
                long_url=long_url, password=make_password(password), user=user, expires_at=expires_at
            )
        else:
            shortener = Shortener.objects.create(long_url=long_url, user=user, expires_at=expires_at)
        return shortener

    def update(self, instance: Shortener, validated_data: dict):
        instance.long_url = validated_data.get("long_url", instance.long_url)
        instance.expires_at = validated_data.get("expires_at", instance.expires_at)
        short_url = instance.short_url
        if (
            isinstance(instance, PasswordProtectedShortener)
            or (len(short_url) == 9 and short_url.startswith("pw"))
        ) and "password" in validated_data:
            password = validated_data.get("password")
            if password:
                instance.password = make_password(password)
        instance.save()
        return instance


class PrivateShortenerSerializer(ShortenerSerializer):
    class Meta(ShortenerSerializer.Meta):
        model = PrivateShortener
        fields = ["short_url", "created", "updated", "times_followed", "user", "expires_at", "is_active"]
        read_only_fields = ["short_url", "created", "updated", "times_followed", "user", "is_active"]


class PrivateShortenerSerializerCreator(ShortenerSerializerCreator):
    class Meta(
        ShortenerSerializerCreator.Meta
        if hasattr(ShortenerSerializerCreator, "Meta")
        else object
    ):
        fields = ["long_url", "is_private", "expires_at"]  # is_private is implicitly True

    def create(self, validated_data):
        validated_data["is_private"] = True
        return super().create(validated_data)


class PasswordProtectedShortenerSerializer(ShortenerSerializer):
    class Meta(ShortenerSerializer.Meta):
        model = PasswordProtectedShortener
        fields = ["short_url", "created", "updated", "times_followed", "user", "expires_at", "is_active"]
        read_only_fields = [
            "short_url",
            "created",
            "updated",
            "times_followed",
            "user",
            "is_active",
        ]  # Don't expose the hash


class PasswordProtectedShortenerSerializerCreator(ShortenerSerializerCreator):
    password = serializers.CharField(write_only=True, required=True)

    class Meta(
        ShortenerSerializerCreator.Meta
        if hasattr(ShortenerSerializerCreator, "Meta")
        else object
    ):
        fields = [
            "long_url",
            "has_password",
            "password",
            "expires_at",
        ]  # has_password is implicitly True

    def create(self, validated_data):
        validated_data["has_password"] = True
        password = validated_data.pop("password")
        validated_data["password"] = make_password(password)
        return super().create(validated_data)
