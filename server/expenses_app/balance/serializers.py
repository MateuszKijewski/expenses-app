from rest_framework import serializers

from core import models


class IncomeSerializer(serializers.ModelSerializer):
    """Serializes income model"""

    class Meta:
        model = models.Income
        fields = ('user', 'source', 'is_archived', 'amount', 'add_date')
        extra_kwargs = {
            'user': {'read_only': True},
            'is_archived': {'read_only': True}
        }