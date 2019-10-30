from django.http import HttpResponse

from rest_framework import viewsets, mixins, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Operation, LimitedCategory, Saving

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
        if (serializer.validated_data['amount'] > 0):
            serializer.save(user=self.request.user)
        else:
            category = serializer.validated_data['category']
            try:
                limited_category = LimitedCategory.objects.get(category=category)
                limited_category.amount += serializer.validated_data['amount']
                limited_category.save()        
                serializer.save(user=self.request.user)
            except LimitedCategory.DoesNotExist:
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
            return Response({'message': 'Objects were succesfuly deleted'})


class LimitedCategoryViewSet(viewsets.ModelViewSet):
    """Manager for the limited categories"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.LimitedCategorySerializer
    queryset = LimitedCategory.objects.all()

    def get_queryset(self):
        """Return objects for the currently authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create new category"""
        serializer.save(user=self.request.user, amount=self.request.data['limit'])


class SavingViewSet(viewsets.ModelViewSet):
    """Manaager for savings"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SavingSerializer
    queryset = Saving.objects.all()

    def get_queryset(self):
        """Return objects for the currently authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create new saving"""
        serializer.save(user=self.request.user, current_amount=0)


class SavingOperations(generics.GenericAPIView):
    """View for adding and withdrawing money from savings"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Saving.objects.all()

    def get_queryset(self):
        saving_id = self.kwargs.get('saving_id')
        return self.queryset(user=self.request.user, id=saving_id)

    def get(self, request):
        """Retrieve saving info"""
        data = {
            'saving': serializers.SavingSerializer(self.queryset).data
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Post amount that you want to withdraw or add to your saving"""
        serializer = serializers.SavingOperationSerializer(data=request.data)
        if serializer.is_valid():
            value = serializer.validated_data.get('value')
            if value > 0:
                pass
        return Response({"message": "tbc"})
