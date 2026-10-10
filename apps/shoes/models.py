from django.db import models
from apps.Category.models import Category
# Create your models here.

class ShoeCompany(models.Model):
    """ Brand / Manufucturter"""

    name  = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Shoe Companies"
        ordering = ['name']

    def __str__(self):
        return self.name


class Shoe(models.Model):
    class Gender (models.TextChoices):
        MALE = "MALE",'Male'
        FEMALE = "FEMALE",'Female'
        UNISEX = "UNISEX",'Unisex'
        CHILDREN = "CHILDREN",'Children' 

    name = models.CharField(max_length=150, )
    model_number = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(
            Category,on_delete=models.PROTECT,related_name='shoes')

    company = models.ForeignKey(
            ShoeCompany,on_delete=models.PROTECT,related_name='shoes')

    material = models.CharField(max_length=150, blank=True)
    gender = models.CharField(
            max_length=10,choices=Gender.choices,default=Gender.UNISEX)


    description = models.TextField(blank=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='shoes/', blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]  

    def __str__(self):
        return f"{self.company.name} ({self.name})"

    @property
    def total_stock(self):
        return sum(v.quantity for v in self.variants.all())



class ShoeVariant(models.Model):
    shoe = models.ForeignKey(
        Shoe,on_delete=models.CASCADE,related_name='variants')

    size  = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=0)
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Optional price ovveride for this size"
        )
     
    
    
    
    class Meta:
        unique_together = ('shoe', 'size')
        ordering = ['shoe','size']


    def __str__(self):
        return f"{self.shoe} - Size {self.size}"

    @property
    def effective_price(self):
        return self.selling_price if self.selling_price is not None  else self.shoe.selling_price
    