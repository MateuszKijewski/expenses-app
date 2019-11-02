from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


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

    def get_balance(self):
        """Gets users balance"""
        balance = 0
        for operation in Operation.objects.filter(user=self):
            balance += operation.amount
        return balance

class Operation(models.Model):
    """Database model for operation"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
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
    SAVING = 'Saving'
    OTHERS = 'Others'

    CATEGORY_CHOICES = [
        (SHOPPING, 'Shopping'),
        (FOODDRINK, 'Food & Drink'),
        (GROCERIES, 'Groceries'),
        (ENTERTAINMENT, 'Entertainment'),
        (BILL, 'Bill'),
        (SUBSCRIPTION, 'Subscription'),
        (INCOME, 'Income'),
        (SAVING, 'Saving'),
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


class ReccuringPayment(models.Model):
    """Database model for limited reccuring payments"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    source = models.CharField(max_length=255)
    paid_until = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2
    )
    paid = models.BooleanField(default=False)

    BILL = 'Bill'
    SUBSCRIPTION = 'Subscription'

    CATEGORY_CHOICES = [
        (BILL, 'Bill'),
        (SUBSCRIPTION, 'Subscription')
    ]
    category = models.CharField(
        max_length=len(SUBSCRIPTION),
        choices=CATEGORY_CHOICES
    )

    def __str__(self):
        """String representation of a model"""
        return self.source

    def until_payment(self):
        """Checks how many days until payment"""
        today = date.today().strftime("%d")
        if self.paid:
            return "It's already paid"
        return self.paid_until - today


class LimitedCategory(models.Model):
    """Database model for limited categories"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    limit = models.DecimalField(
        max_digits=19,
        decimal_places=2
    )
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2
    )
    SHOPPING = 'Shopping'
    FOODDRINK = 'Food & Drink'
    GROCERIES = 'Groceries'
    ENTERTAINMENT = 'Entertainment'
    OTHERS = 'Others'

    CATEGORY_CHOICES = [
        (SHOPPING, 'Shopping'),
        (FOODDRINK, 'Food & Drink'),
        (GROCERIES, 'Groceries'),
        (ENTERTAINMENT, 'Entertainment'),
        (OTHERS, "Others")
    ]
    category = models.CharField(
        max_length=len(FOODDRINK),
        choices=CATEGORY_CHOICES,
        default=None
    )

    def __str__(self):
        """Return string representation"""
        return self.category

    def set_initial_value(self):
        """Sets the value according to limit"""
        self.amount = self.limit


class Saving(models.Model):
    """Database model for savings"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2
    )
    current_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2
    )
    VACATION = 'Vacation'
    TRIP = 'Trip'
    MOTORISATION = 'Motorisation'
    BUSINESS = 'Business'
    OTHERS = 'Others'

    CATEGORY_CHOICES = [
        (VACATION, 'Vacation'),
        (TRIP, 'Trip'),
        (MOTORISATION, 'Motorisation'),
        (TRIP, 'Trip'),
        (BUSINESS, 'Business'),
        (OTHERS, 'Others')
    ]

    category = models.CharField(
        max_length=len(MOTORISATION),
        choices=CATEGORY_CHOICES,
        default=None
    )

    def __str__(self):
        """Return string representation"""
        return self.name