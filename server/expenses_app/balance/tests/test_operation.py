from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Operation

from balance.serializers import OperationSerializer

BALANCE_URL = reverse('balance:operation-list')
OPERATION_DELETE_URL = reverse('balance:delete')


class PublicOperationApiTests(TestCase):
    """Test the publicly available operation"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access operation"""
        res = self.client.get(BALANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOperationApiTests(TestCase):
    """Test the private operation actions"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test123@gmail.com',
            password='test123',
            tel_number='123456789'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_user_retrieve_list(self):
        """Test if user is able to retrieve his operation"""
        Operation.objects.create(
            user = self.user,
            source = 'ubereats',
            amount = 20.00,
            category = 'Shopping',
            method = 'Bank transfer'
        )
        Operation.objects.create(
            user = self.user,
            source = 'mousepad',
            amount = 10.00,
            category = 'Shopping',
            method = 'Bank transfer'
        )

        res = self.client.get(BALANCE_URL)

        operations = Operation.objects.all().order_by('-source')
        serializer = OperationSerializer(operations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_operations_related_to_user(self):
        """Test if retrieved operations belong to user"""
        new_user = get_user_model().objects.create_user(
            email='else@gmail.com',
            password='asd123',
            tel_number='987654321'
        )
        Operation.objects.create(
            user=new_user,
            source='new user thing',
            amount=5.00,
            category = 'Shopping',
            method = 'Bank transfer'
        )
        operation = Operation.objects.create(
            user=self.user,
            source='telephone',
            amount=500.00,
            category = 'Shopping',
            method = 'Bank transfer'
        )

        res = self.client.get(BALANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['source'], operation.source)

    def test_create_operation_succesfull(self):
        """Test creating an operation object"""
        payload = {
            'source': 'work',
            'amount': 3200,
            'category': 'Shopping',
            'method': 'Bank transfer'
        }
        res = self.client.post(BALANCE_URL, payload)
        exists = Operation.objects.filter(
            user=self.user,
            source=payload['source'],
            amount=payload['amount']
        ).exists()

        self.assertTrue(exists)
    
    def test_create_operation_invalid(self):
        """Test creating with invalid payload"""
        payload = {
            'source': '',
            'amount': '',
            'category': '',
            'method': ''
        }
        res = self.client.post(BALANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_getting_balance(self):
        """Test getting balance related to users operations"""
        operation_add = Operation.objects.create(
            user=self.user,
            source='OLX',
            amount=3400.00,
            category = 'Income',
            method = 'Bank transfer'
        )
        operation_delete = Operation.objects.create(
            user=self.user,
            source='telephone',
            amount= -1400.00,
            category = 'Others',
            method = 'Bank transfer'
        ) 
        res = self.client.get(BALANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(float(res.data[0]['amount']) + 
                        float(res.data[1]['amount']), 2000.00)

    def test_operation_deleting_success(self):
        """Test deleting objects"""
        operation = Operation.objects.create(
            user=self.user,
            source='spotify',
            amount= -30,
            category= 'Bill',
            method = 'Bank transfer'
        )
        res = self.client.post(OPERATION_DELETE_URL, {"ids":[1]})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(BALANCE_URL)

        self.assertEqual(len(res.data), 0)
    
    def test_deleting_nonexistent_operations(self):
        """Test deleting with invalid id"""
        res = self.client.post(OPERATION_DELETE_URL, {"ids":[1]})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)