from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import ReccuringPayment

from periodic.serializers import ReccuringPaymentSerializer

RECCURING_PAYMENT_URL = reverse('periodic:reccurent-list')


class PublicOperationApiTests(TestCase):
    """Test the publicly available payments"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access operation"""
        res = self.client.get(RECCURING_PAYMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReccuringPaymentApiTest(TestCase):
    """Test the private payment actions"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test123@gmail.com',
            password='test123',
            tel_number='123456789'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_user_retrieve_list(self):
        """Test if user is able to retrieve his payment"""
        ReccuringPayment.objects.create(
            user = self.user,
            source = 'water',
            amount = -20.00,
            category = 'Bills',
            paid_until = '2019-12-12'
        )
        ReccuringPayment.objects.create(
            user = self.user,
            source = 'netflix',
            amount = -10.00,
            category = 'Bills',
            paid_until = '2019-12-12'
        )

        res = self.client.get(RECCURING_PAYMENT_URL)

        payments = ReccuringPayment.objects.all().order_by('-source')
        serializer = ReccuringPaymentSerializer(payments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_payments_related_to_user(self):
        """Test if retrieved payments belong to user"""
        new_user = get_user_model().objects.create_user(
            email='else@gmail.com',
            password='asd123',
            tel_number='987654321'
        )
        ReccuringPayment.objects.create(
            user = new_user,
            source = 'netflix',
            amount = -20.00,
            category = 'Bills',
            paid_until = '2019-12-12'
        )
        payment = ReccuringPayment.objects.create(
            user = self.user,
            source = 'water',
            amount = -10.00,
            category = 'Bills',
            paid_until = '2019-12-12'
        )

        res = self.client.get(RECCURING_PAYMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['source'], payment.source)

    def test_create_operation_succesfull(self):
        """Test creating an operation object"""
        payload = {
            'source': 'Food',
            'amount': -200,
            'category': 'Bills',
            'paid_until': '2019-11-11'
        }
        res = self.client.post(RECCURING_PAYMENT_URL, payload)
        exists = ReccuringPayment.objects.filter(
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
            'category': ''
        }
        res = self.client.post(RECCURING_PAYMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)