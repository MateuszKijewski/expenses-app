from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializes user models"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name', 'tel_number',)
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'tel_number': {'min_length': 9}
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)