from django.db import models
from user.models import User


# Create your models here.
class Products(models.Model):
    author = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.IntegerField()
    description = models.CharField(max_length=2000)

    # date_added = models.DateTimeField(auto_now_add=True)

    def get_title(self):
        return self.title


class Cart(models.Model):
    owner = models.OneToOneField(to=User, on_delete=models.CASCADE)
    products = models.ManyToManyField(to=Products)
    quantity = models.IntegerField(null=True)


class Order(models.Model):
    owner = models.OneToOneField(to=User, on_delete=models.CASCADE)
    products = models.ManyToManyField(to=Products)
    address = models.CharField(max_length=200, null=True)
    phone = models.BigIntegerField(null=True)
    total_price = models.IntegerField(null=True)
    total_items = models.IntegerField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
