from django.http import HttpResponse

from rest_framework import viewsets, mixins
from rest_framework.views import  APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import ReccuringPayment, Operation

from periodic import serializers


class ReccurentPaymentViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):
    """Manage operations in the database"""
    serializer_class = serializers.ReccuringPaymentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = ReccuringPayment.objects.all()

    def get_queryset(self):
        """Return objects for the currently authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Return objects for the currently authenticated user"""
        serializer.save(user=self.request.user)


class ReccurentMakePayment(APIView):
    """Uses ids of payments that user wants to make"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = ReccuringPayment.objects.all()

    def post(self, request):
        """Set posted unpaid payments to paid"""
        serializer = serializers.ReccuringMakePaymentSerializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data.get('ids')
            for value in ids:
                value = int(value)
                try:
                    payment = self.queryset.filter(user=self.request.user, pk=value).get()
                except ReccuringPayment.DoesNotExist:
                    return Response({"message": "Such payment does not exist"})

            for value in ids:
                payment = self.queryset.filter(user=self.request.user, pk=value).get()
                if payment.paid:
                    return Response({"message": f"{payment.source} is already paid"})
                operation = Operation.objects.create(
                    user=request.user,
                    source=payment.source,
                    amount=-payment.amount,
                    category=payment.category
                )
                operation.save()
                payment.paid = True
                payment.save()
            return Response({"message": "You've successfully paid"})
        return HttpResponse(status=400)