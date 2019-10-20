from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Income

from balance.serializers import IncomeSerializer

BALANCE_URL = reverse('balance:income-list')


class PublicIncomeApiTests(TestCase):
    """Test the publicly available income"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access income"""
        res = self.client.get(BALANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIncomeApiTests(TestCase):
    """Test the private income actions"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test123@gmail.com',
            password='test123',
            tel_number='123456789'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_user_retrieve_list(self):
        """Test if user is able to retrieve his income"""
        Income.objects.create(
            user = self.user,
            source = 'ubereats',
            amount = 20.00
        )
        Income.objects.create(
            user = self.user,
            source = 'mousepad',
            amount = 10.00
        )

        res = self.client.get(BALANCE_URL)

        incomes = Income.objects.all().order_by('-source')
        serializer = IncomeSerializer(incomes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_incomes_related_to_user(self):
        """Test if retrieved incomes belong to user"""
        new_user = get_user_model().objects.create_user(
            email='else@gmail.com',
            password='asd123',
            tel_number='987654321'
        )
        Income.objects.create(
            user=new_user,
            source='new user thing',
            amount=5.00
        )
        income = Income.objects.create(
            user=self.user,
            source='telephone',
            amount=500.00
        )

        res = self.client.get(BALANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['source'], income.source)

    def test_create_income_succesfull(self):
        """Test creating an income object"""
        payload = {
            'source': 'work',
            'amount': 3200
        }
        res = self.client.post(BALANCE_URL, payload)
        exists = Income.objects.filter(
            user=self.user,
            source=payload['source'],
            amount=payload['amount']
        ).exists()

        self.assertTrue(exists)
    
    def test_create_income_invalid(self):
        """Test creating with invalid payload"""
        payload = {
            'source': '',
            'amount': ''
        }
        res = self.client.post(BALANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)