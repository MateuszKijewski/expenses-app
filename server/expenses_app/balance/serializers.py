from rest_framework import serializers

from core import models


class OperationSerializer(serializers.ModelSerializer):
    """Serializes operation model"""

    class Meta:
        model = models.Operation
        fields = ('id', 'user', 'source', 'is_archived', 'amount', 'add_date',
                    'category', 'method',)
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'is_archived': {'read_only': True}
        }

class DeleteSerializer(serializers.Serializer):
    """Serializes tasks that are about to be deleted"""
    ids = serializers.ListField(
        child=serializers.IntegerField()
    )