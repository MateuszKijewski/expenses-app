from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
                                        PermissionsMixin
from django.conf import settings
from django.core.validators import MinValueValidator


class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    tel_number = models.CharField(max_length=20)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Operation(models.Model):
    """Database model for operation"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )
    source = models.CharField(max_length=255)
    is_archived = models.BooleanField(default=False)
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2
    )
    add_date = models.DateField(auto_now_add=True)

    SHOPPING = 'Shopping'
    FOODDRINK = 'Food & Drink'
    GROCERIES = 'Groceries'
    ENTERTAINMENT = 'Entertainment'
    BILL = 'Bill'
    SUBSCRIPTION = 'Subscription'
    INCOME = 'Income'
    OTHERS = 'Others'

    CATEGORY_CHOICES = [
        (SHOPPING, 'Shopping'),
        (FOODDRINK, 'Food & Drink'),
        (GROCERIES, 'Groceries'),
        (ENTERTAINMENT, 'Entertainment'),
        (BILL, 'Bill'),
        (SUBSCRIPTION, 'Subscription'),
        (INCOME, 'Income'),
        (OTHERS, "Others")
    ]
    category = models.CharField(
        max_length=255,
        choices=CATEGORY_CHOICES,
        default=None
    )
    method = models.CharField(
        max_length=255,
        default='Bank transfer'
    )


    def __str__(self):
        """String representation of an operation"""
        return self.source


"""
class Category():
    name = charfield
    limit = integerfield
    


"""

"""
class ReccuringPayments(models.Model):
    user = ForeignKey
    source = Charfield
    paid_until = DateTime()
    amount = DecimalField

    BILL = 'Bill'
    SUBSCRIPTION = 'Subscription

    CATEGORY_CHOICES = [
        (BILL, 'Bill'),
        (SUBSCRIPTION, 'Subscription)
    ]

"""