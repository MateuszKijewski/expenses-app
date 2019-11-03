from rest_framework import serializers

from core import models


class ReccuringPaymentSerializer(serializers.ModelSerializer):
    """Serializes reccuring payment objects"""

    class Meta:
        model = models.ReccuringPayment
        fields = ('id', 'user', 'source', 'paid_until', 'amount',
                  'paid', 'category',)
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'paid': {'read_only': True}
        }


class ReccuringMakePaymentSerializer(serializers.Serializer):
    """Serializes ids passed to make payments"""
    ids = serializers.ListField(
        child=serializers.IntegerField()
    )