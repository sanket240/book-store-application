from django.db import models


# Create your models here.
class Products(models.Model):
    author = models.CharField(max_length=15)
    title = models.CharField(max_length=30)
    image = models.ImageField(upload_to='pictures/%Y/%m/%d/', max_length=255, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.IntegerField()
    description = models.CharField(max_length=150)
