from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Operation, LimitedCategory

from balance.serializers import OperationSerializer, LimitedCategorySerializer

BALANCE_URL = reverse('balance:operation-list')
OPERATION_DELETE_URL = reverse('balance:delete')
LIMITED_CATEGORIES_URL = reverse('balance:limitedcategory-list')
SAVING_URL = reverse('balance:saving-list')


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

    def test_create_operation_successful(self):
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

    def test_category_list(self):
        """Test if categories are listing correctly"""
        LimitedCategory.objects.create (
            user=self.user,
            category='Groceries',
            limit=250,
            amount=250
        )
        LimitedCategory.objects.create (
            user=self.user,
            category='Food & Drink',
            limit=300,
            amount=250
        )

        res = self.client.get(LIMITED_CATEGORIES_URL)

        categories = LimitedCategory.objects.all().order_by('-category')
        serializer = LimitedCategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_categories_related_to_user(self):
        """Test if retrieved categories belong to user"""
        new_user = get_user_model().objects.create_user(
            email='else@gmail.com',
            password='asd123',
            tel_number='987654321'
        )
        LimitedCategory.objects.create (
            user=new_user,
            category='Groceries',
            limit=250,
            amount=250
        )
        category = LimitedCategory.objects.create (
            user=self.user,
            category='Food & Drink',
            limit=300,
            amount=250
        )

        res = self.client.get(LIMITED_CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['category'], category.category)

    def test_limited_category_expense(self):
        """Test if created expense in limited category subtracts from the amount"""
        payload_category = {
            'category': 'Groceries',
            'limit': '250'
        }

        payload_operation = {
            'source': 'walmart',
            'amount': -30,
            'category': 'Groceries',
            'method': 'Bank transfer'
        }
        res_category = self.client.post(LIMITED_CATEGORIES_URL, payload_category)
        res_operation = self.client.post(BALANCE_URL, payload_operation)

        self.assertEqual(res_category.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_operation.status_code, status.HTTP_201_CREATED)

        res_category = self.client.get(LIMITED_CATEGORIES_URL)
        self.assertEqual(float(res_category.data[0]['amount']), 220.00)

    def test_saving_operations(self):
        """Test if adding and withdrawing from operations works"""
        payload_saving = {
            'name': 'Japan',
            'target_amount': '3000',
            'category': 'Trip'
        }
        payload_operation_1 = {
            'value': 100
        }
        payload_operation_2 = {
            'value': -50
        }

        res_creation = self.client.post(SAVING_URL, payload_saving)
        self.assertEqual(res_creation.status_code, status.HTTP_201_CREATED)

        self.client.post('/api/balance/savings/1/operations/', payload_operation_1)
        res_creation = self.client.get(SAVING_URL)
        self.assertEqual(float(res_creation.data[0]['current_amount']), 100.00)

        self.client.post('/api/balance/savings/1/operations/', payload_operation_2)
        res_creation = self.client.get(SAVING_URL)
        self.assertEqual(float(res_creation.data[0]['current_amount']), 50.00)



