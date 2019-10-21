from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@gmail.com', password='test123'):
    """Create sample user"""
    tel_number = '123456789'
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        tel_number=tel_number
    )


class ModelTests(TestCase):
    
    def test_create_user_with_email_succseful(self):
        """Test creating a new user with an email is succesful"""
        email = 'test@gmail.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            tel_number='123456789'
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
    
    def test_new_user_email_normalized(self):
        """Tests if email is normalized"""
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='test123',
            tel_number='123456789'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Tests raising error when no email is provided"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_creating_superuser(self):
        """Tests creation of superuser"""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_operation_str(self):
        """Test the operation string representation"""
        operation = models.Operation.objects.create(
            user = sample_user(),
            source = 'ubereats',
            amount = 20.00,
            category= 'Groceries',
            method='Bank transfer'
        )

        self.assertEqual(str(operation), operation.source)