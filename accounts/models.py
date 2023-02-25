from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from jsignature.fields import JSignatureField
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, username, name, surname, email, phone, password=None):
        
        if not username:
            raise ValueError('User must have username')
        if not name:
            raise ValueError("User must have a name")
        if not surname:
            raise ValueError("User must have a surname")
        if not phone:
            raise ValueError("User must have a phone")
               
        user = self.model(
            username = username,
            name = name,
            surname = surname,
            phone = phone,
            email = email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, username, name, surname, email, phone, password=None):
        """
        Creates and saves a superuser with the given username, email, first_name, password.
        """
        user = self.create_user(
            username = username,
            name = name,
            surname = surname,
            email =email,
            phone = phone,
            password = password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user    


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=100, unique=True, validators=[username_validator], error_messages={'unique': "A user with that username already exists.",})
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = PhoneNumberField(max_length=15, unique=True, help_text="Phone Number With Country Code")
    mall = models.ForeignKey('Malls', on_delete=models.CASCADE, null=True, blank=True, related_name='user')
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'surname', 'email', 'phone']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class BaseModel(models.Model):
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  class Meta:
    abstract = True


class Customers(BaseModel):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    cellphone = PhoneNumberField(max_length=15, unique=True, help_text="Phone Number With Country Code")
    email = models.EmailField(max_length=100, unique=True)
    age = models.PositiveIntegerField(max_length=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')


    def __str__(self):
        return f'{self.name} {self.surname}'

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


class Malls(BaseModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Mall'
        verbose_name_plural = 'Malls'


class Inventory(BaseModel):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    mall_assigned = models.ForeignKey(Malls, on_delete=models.CASCADE, related_name='inventory')
    booking_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'


class Remark(BaseModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='remark')
    remarkcomment=models.TextField(max_length=400)


class Service(BaseModel):
    name = models.CharField(max_length=100)
    time = models.FloatField(help_text='Time is in minute')
    price = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'


class Income(BaseModel):
    CHOICES = [
        ("Card", 'Card'),
        ("Cash", 'Cash'),
    ]
    mall_assigned = models.ForeignKey(Malls, on_delete=models.CASCADE, related_name='income_mall')
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='income_customer')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='income_service')
    equipment = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='income_inventory')
    payment_method = models.CharField(max_length=100, choices=CHOICES)
    payment_date = models.DateTimeField(default=timezone.now())
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

                                                                                                                                                                                                                                                                                                                                                                                                                                                     

class ResponsiveLetter(BaseModel):
    customer = models.ForeignKey(Customers, null=True, blank=True, on_delete=models.CASCADE, related_name='responsive_letter_customer')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='responsive_letter_user')
    description = models.TextField(max_length=4000)
    date = models.DateTimeField(default=timezone.now())
    signature = JSignatureField(null=True, blank=True)

    class Meta:
        verbose_name = 'Responsive Letter'
        verbose_name_plural = 'Responsive Letter'


class PrivacyPolicy(BaseModel):
    heading = models.CharField(max_length=200)
    description = models.TextField(max_length=4000)

    class Meta:
        verbose_name = 'Privacy Policy'
        verbose_name_plural = 'Privacy Policies'

