from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.

class Role(models.TextChoices):
    OWNER = "OWNER","Owner"
    MANAGER="MANAGER","Manager"
    CASHIER ="CASHIER","Cashier"
    STOCK_MANAGER="STOCK_MANAGER","Stock Manager"


class User(AbstractUser):

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)
    phone =models.CharField(max_length=20,blank=True)
    