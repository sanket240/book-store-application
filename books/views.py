# Create your views here.
from .serializers import ProductSerializer
from .models import Products
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, RetrieveAPIView, \
    GenericAPIView, RetrieveUpdateAPIView

from rest_framework import permissions, status, views
import logging
from psycopg2 import OperationalError
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('django')


class ProductCreateView(ListCreateAPIView):
    serializer_class = ProductSerializer

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


class ProductOperationsView(GenericAPIView):
    serializer_class = ProductSerializer
    lookup_field = "id"
    queryset = Products.objects.all()

    def delete(self, request, id):
        """
                This api is for deleting of new products
                @param request: ID of the product
                @return: response of deleted product
        """
        try:

            product = Products.objects.filter(id=id)
            product.delete()
            logger.info("Product is Deleted Permanently, from delete()")
            return Response({'response': 'Note is Deleted'}, status=200)
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

    def put(self, request, id):
        """
                This api is for updating of new products
                @param request: ID of the product
                @return: response of updated product
        """
        try:
            data = request.data
            instance = Products.objects.get(id=id)
            serializer = ProductSerializer(instance, data=data)
            if serializer.is_valid():
                serializer.save(id=id)
                logger.info("Product updated successfully, from put()")
                return Response({'Message': 'Note updated successfully'}, status=201)
            return Response({'Error': 'Failed to update note'}, status=status.HTTP_400_BAD_REQUEST)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to update product'}, status=status.HTTP_400_BAD_REQUEST)
