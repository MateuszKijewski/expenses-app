from django.http import HttpResponse

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.models import Operation

from balance import serializers


class OperationViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    """Manage operations in the database"""
    serializer_class = serializers.OperationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Operation.objects.all()

    def get_queryset(self):
        """Return objects for the currently authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create new action"""
        serializer.save(user=self.request.user)

class OperationDelete(APIView):
    """Handle operations deleting"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Operation.objects.all()

    def post(self, request, format=None):
        """Deletes objects that user posted"""
        serializer = serializers.DeleteSerializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data.get('ids')            
            for value in ids:
                value = int(value)
                try:
                    operation = self.queryset.filter(user=self.request.user, pk=value).get()
                except Operation.DoesNotExist:
                    return HttpResponse(status=400)
            for value in ids:
                operation = self.queryset.filter(pk=value, user=self.request.user).get()
                operation.delete()
            return Response({'message': 'Objects were succesfully deleted'})