# Create your views here.
from django.shortcuts import get_object_or_404
from .serializers import ProductSerializer, WishListSerializer
from .models import Products, Order
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, RetrieveUpdateAPIView, CreateAPIView
from user.models import User
from rest_framework import permissions, status, views
import logging
from psycopg2 import OperationalError
from rest_framework.exceptions import ValidationError
from .models import Cart, WishList
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse
from user.utils import Util

logger = logging.getLogger('django')


class ProductCreateView(ListCreateAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        """
                This api is for creation of new notes
                @param request: title and description of notes
                @return: response of created notes
        """
        try:
            serializer.save()
            return Response({'Message': 'Product Created Successfully'}, status=status.HTTP_200_OK)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to create product'}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        try:
            return Products.objects.all()
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to get product'}, status=status.HTTP_400_BAD_REQUEST)


class ProductOperationsView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    lookup_field = "id"
    queryset = Products.objects.all()

    def perform_destroy(self, instance):
        """
                This api is for deleting of new products
                @param request: ID of the product
                @return: response of deleted product
        """
        try:
            instance.delete()
            logger.info("Product is Deleted Permanently, from delete()")
            return Response({'response': 'Note is Deleted'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to delete product,Please try again later'},
                            status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        """
                This api is for updating of new products
                @param request: ID of the product
                @return: response of updated product
        """
        try:
            serializer.save()
            return Response({'Message': 'Note updated successfully'}, status=status.HTTP_200_OK)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to update product'}, status=status.HTTP_400_BAD_REQUEST)


class AddToCartView(CreateAPIView):
    """
            This api is for adding products into cart
            @param id: id of the product
            @return: response of added product into cart
    """
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"

    def post(self, request, id):
        quantity = request.data.get('quantity')
        try:
            owner = User.objects.get(id=self.request.user.id)
            product = Products.objects.get(id=id)
            cart = Cart.objects.get(owner=owner)
            cart.products.add(product)
            cart.quantity = quantity
            cart.save()
            return Response({'Message': 'Added To cart'}, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(owner=owner)
            cart.products.add(product)
            cart.quantity = quantity
            cart.save()
            return Response({'Message': 'Added To cart'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.exception(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e)
            return Response({'Message': 'Failed to add to cart'}, status=status.HTTP_400_BAD_REQUEST)


class SearchAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
                This api is for searching products
                @param search_key: value to be searched
                @return: response of search key
        """
        try:
            search_key = self.kwargs['item']
            logger.info("Data Incoming from the database")
            return Products.objects.filter(Q(title__contains=search_key) | Q(author__contains=search_key))
        except OperationalError as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)


class DisplayBySortedProducts(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_value(self, value):
        switcher = {
            'price-asc': 'price', 'price-desc': '-price', 'author-asc': 'author', 'author-desc': '-author',
            'title-asc': 'title', 'title-desc': '-title', 'quantity-asc': 'quantity', 'quantity-desc': '-quantity'
        }
        return switcher.get(value, "title")

    def get_queryset(self):
        """
                This api is for sorting the products based on params
                @param type: type of parameter to sort
                @return: response of sorted products
        """
        try:
            type = self.kwargs['type']
            value = self.get_value(type)
            return Products.objects.all().order_by(value)
        except OperationalError as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Error Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class PlaceOrderAPIView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_order_object(self, owner):
        try:
            owner = User.objects.get(id=owner.id)
            order = Order.objects.get(owner=owner)
            return order

        except Order.DoesNotExist:
            order = Order.objects.create(owner=owner)
            return order

    def post(self, request):
        """
                    This api is for placing the order from the cart
                    @return: response of ordered products
        """
        total_price = 0
        total_items = 0
        try:
            owner = self.request.user
            order = self.get_order_object(owner)
            address = request.data.get('address')
            phone = request.data.get('phone')
            cart = Cart.objects.filter(owner=self.request.user)
            owner = User.objects.get(id=self.request.user.id)
            if cart:
                cart_list = cart.values('products')
                for items in range(len(cart_list)):
                    product_id = cart_list[items]['products']
                    product = Products.objects.get(id=product_id)
                    cart_object = Cart.objects.get(products=product)
                    order.products.add(product)
                    order.save()
                    total_price = total_price + (product.price * cart_object.quantity)
                    total_items = total_items + 1
                order.total_price = total_price
                order.total_items = total_items
                order.address = address
                order.phone = phone
                order.save()
                email_body = 'Hi ' + str(owner.username) + \
                             ' your order with id:' + str(
                    order.id) + ' has been placed successfully' + '\n Total items are:' + str(
                    total_items) + '\n Total price is:' + str(total_price)
                data = {'email_body': email_body, 'to_email': owner.email,
                        'email_subject': 'Order Delivered'}
                Util.send_email(data)
                return Response({'Message': 'Product added successully'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.exception(e, exc_info=True)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e, exc_info=True)
            return Response({'Message': 'Failed to add to cart'}, status=status.HTTP_400_BAD_REQUEST)


class AddToWishList(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WishListSerializer
    pagination_class = PageNumberPagination
    lookup_field = "id"

    def get_wish_list_object(self, owner):
        try:
            owner = User.objects.get(id=owner.id)
            wish_list = WishList.objects.get(owner=owner)
            return wish_list
        except WishList.DoesNotExist:
            wish_list = WishList.objects.create(owner=owner)
            return wish_list

    def post(self, request, id):
        """
                    This api is for adding the products into wish list
                    @param id: id of product
                    @return: response of wish list products
        """
        try:
            owner = self.request.user
            wish_list = self.get_wish_object(owner)
            product = Products.objects.get(id=id)
            wish_list.products.add(product)
            wish_list.save()
            return Response({'Message': 'Added To Wish List'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.exception(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e)
            return Response({'Message': 'Failed to add to wish list'}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
                    This api is for getting the products from wish list of particular user
                    @return: response of wish list products
        """
        try:
            owner = User.objects.get(id=self.request.user.id)
            return WishList.objects.filter(owner=owner)
        except OperationalError as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Error Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
