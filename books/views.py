# Create your views here.
from django.shortcuts import get_object_or_404
from .serializers import ProductSerializer
from .models import Products, Order
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, RetrieveUpdateAPIView, CreateAPIView
from user.models import User
from rest_framework import permissions, status, views
import logging
from psycopg2 import OperationalError
from rest_framework.exceptions import ValidationError
from .models import Cart
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponse

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
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"

    def post(self, request, id):
        try:
            owner = User.objects.get(id=self.request.user.id)
            product = Products.objects.get(id=id)
            cart = Cart.objects.get(owner=owner)
            cart.products.add(product)
            cart.save()
        except Cart.DoesNotExist:
            cart = Cart.objects.create(owner=owner)
            cart.products.add(product)
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
        """ Get all notes of particular User """
        try:
            search_key = self.kwargs['item']
            logger.info("Data Incoming from the database")
            return Products.objects.filter(Q(title__contains=search_key) | Q(author__contains=search_key))
        except OperationalError as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)


class DisplayByOrder(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            type = self.kwargs['type']
            if type == 'price-low':
                return Products.objects.all().order_by('price')
            elif type == 'price-high':
                return Products.objects.all().order_by('-price')
            elif type == 'author':
                return Products.objects.all().order_by('author')
            elif type == 'title':
                return Products.objects.all().order_by('title')
            elif type == 'quantity':
                return Products.objects.all().order_by('quantity')
        except OperationalError as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Error Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class PlaceOrderAPIView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        total_price = 0
        total_quantity = 0
        address = request.data.get('address')
        phone = request.data.get('phone')
        owner = User.objects.get(id=self.request.user.id)
        try:
            cart = Cart.objects.filter(owner=owner)
            order = Order.objects.create(owner=owner, address=address, phone=phone)
            if cart:
                cart_list = cart.values('products')
                for items in range(len(cart_list)):
                    product_id = cart_list[items]['products']
                    product = Products.objects.get(id=product_id)
                    order.products.add(product)
                    order.save()
                    total_price = total_price + product.price
                    total_quantity = total_quantity + 1
                print(total_price)
                print(total_price)
                order.total_price = total_price
                order.total_quantity = total_quantity
                order.save()
                return Response({'Message': 'Product added successully'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.exception(e, exc_info=True)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(e, exc_info=True)
            return Response({'Message': 'Failed to add to cart'}, status=status.HTTP_400_BAD_REQUEST)
