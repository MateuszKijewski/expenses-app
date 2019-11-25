from itertools import chain

from django.http import HttpResponse

from rest_framework import viewsets, mixins, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Operation, LimitedCategory, Saving, ReccuringPayment

from balance import serializers
from periodic.serializers import ReccuringPaymentSerializer


class DashboardAPIView(APIView):
    """Show application dashboard"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        reccuring_payments_queryset = ReccuringPayment.objects.filter(user=self.request.user)
        close_payments_ids = [
            payment.id
            for payment in reccuring_payments_queryset
            if payment.until_payment() < 20
        ]
        reccuring_payments_queryset = reccuring_payments_queryset.filter(pk__in=close_payments_ids)[:4]
        limited_categories_queryset = LimitedCategory.objects.filter(user=self.request.user)[:4]
        saving_categories_queryset = Saving.objects.filter(user=self.request.user)[:5]

        result_list = list(chain(
            reccuring_payments_queryset,
            limited_categories_queryset,
            saving_categories_queryset
        ))
        results = list()
        for entry in result_list:
            item_type = entry.__class__.__name__.lower()
            if isinstance(entry, ReccuringPayment):
                serializer = ReccuringPaymentSerializer(entry)
            if isinstance(entry, LimitedCategory):
                serializer = serializers.LimitedCategorySerializer(entry)
            if isinstance(entry, Saving):
                serializer = serializers.SavingSerializer(entry)

            results.append({'item_type': item_type, 'data': serializer.data})
        results.append({'balance': self.request.user.get_balance()})

        return results

    def get(self, request):
        return Response(self.get_queryset())


class OperationViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin):
    """Manage operations in the database"""
    serializer_class = serializers.OperationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Operation.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Object created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        """Return objects for the currently authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-add_date')

    def perform_create(self, serializer):
        """Create new action"""
        if serializer.validated_data['amount'] > 0:
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

    def get(self, request):
        balance = request.user.get_balance()
        return Response({"balance": balance})

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Object created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Object created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

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
    serializer_class = serializers.SavingOperationSerializer

    def get_queryset(self, request):
        """Gets the currently authenticated user object"""
        return self.queryset(user=self.request.user)

    def post(self, request, saving_id, format=None):
        """
        Manipulates saving value, creating operation
        objects depending on the actions taken
        """
        serializer = serializers.SavingOperationSerializer(data=request.data)

        if serializer.is_valid():
            value = serializer.validated_data.get('value')
            obj = self.queryset.get(id=saving_id)

            if value > 0:
                """Deposit"""
                obj.current_amount += value
                if obj.current_amount == obj.target_amount:
                    """Finished saving"""
                    obj.delete()
                    return Response({"message": "Congratulations! You've achieved your goal"})
                elif obj.current_amount > obj.target_amount:
                    """Added too much with the last saving"""
                    excess = obj.current_amount - obj.target_amount
                    operation = Operation.objects.create(
                        user=request.user,
                        source=f'{obj.name} - excess',
                        amount=excess,
                        category='Saving',
                        method='-'
                    )
                    obj.delete()
                    operation.save()
                    return Response({"message": "Congratulations! You've achieved your goal"
                                                "(exceed amount has been returned to your account)"})
                operation = Operation.objects.create(
                    user=request.user,
                    source=f'{obj.name} - saving',
                    amount=value,
                    category='Saving',
                    method='-'
                )
                obj.save()
                operation.save()
                return Response({"message": "Successfully added!"})

            elif value < 0:
                """Withdraw"""
                obj.current_amount += value
                if obj.current_amount < 0:
                    """Withdrawing more than you have saved"""
                    return Response({"message": "You can't withdraw more than you have saved"})
                operation = Operation.objects.create(
                    user=request.user,
                    source=f'{obj.name} - withdraw',
                    amount=value,
                    category='Saving',
                    method='-'
                )
                obj.save()
                operation.save()
                return Response({"message": "Successfully withdrawn!"})
        return Response({'message': 'Provided amount was invalid'}, status.HTTP_400_BAD_REQUEST)
