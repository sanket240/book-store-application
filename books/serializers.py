from .models import Products, WishList
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['author', 'title', 'image', 'quantity', 'price', 'description']


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ['owner', 'products']
