from rest_framework import serializers

from core import models


class ReccuringPaymentSerializer(serializers.ModelSerializer):
    """Serializes reccuring payment objects"""

    class Meta:
        model = models.ReccuringPayment
        fields = ('id', 'user', 'source', 'paid_until', 'amount', 'category',)
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True}
        }