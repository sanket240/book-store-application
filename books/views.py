# Create your views here.

from .serializers import ProductSerializer
from .models import Products
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, RetrieveAPIView, \
    GenericAPIView, ListAPIView, RetrieveUpdateAPIView
from user.models import User
from rest_framework import permissions, status, views
import logging
from psycopg2 import OperationalError
from rest_framework.exceptions import ValidationError
from .models import Cart
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

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


class AddToCartView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"

    def post(self, request, id):
        try:
            owner = User.objects.get(id=self.request.user.id)
            product = Products.objects.get(id=id)
            cart = Cart.objects.get(owner=owner)
            if cart:
                cart.products.add(product)
                cart.save()
            else:
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

    def get_queryset(self):
        try:
            logger.info("Data Incoming from the database")
            return Cart.objects.filter(owner=self.request.user.id)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)


class OrderAscendingAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            return Products.objects.all().order_by('price')
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to get product'}, status=status.HTTP_400_BAD_REQUEST)


class OrderDescendingAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            return Products.objects.all().order_by('-price')
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to get product'}, status=status.HTTP_400_BAD_REQUEST)


class SearchAPIView(ListCreateAPIView):
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """ Get all notes of particular User """
        try:
            search_key = self.request.data.get('value')
            logger.info("Data Incoming from the database")
            return Products.objects.filter(Q(title__contains=search_key) | Q(author__contains=search_key))
        except OperationalError as e:
            logger.error(e, exc_info=True)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
