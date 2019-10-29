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

class LimitedCategorySerializer(serializers.ModelSerializer):
    """Serializes limited categories model"""
    
    class Meta:
        model = models.LimitedCategory
        fields = ('id', 'user', 'limit', 'amount', 'category')
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'amount': {'read_only': True}
        }