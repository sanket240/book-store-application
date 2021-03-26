from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
import json
from rest_framework.test import APITestCase
from user.models import User
from django.conf import settings
import jwt

CONTENT_TYPE = 'application/json'


class ProductAPITest(APITestCase):
    def setUp(self):
        self.client = Client()

        self.create_products_valid_payload = {
            "author": "Stephen King'",
            "title": "The Dark Tower VII'",
            "image": "http://books.google.com/books/content?id=Geq0uKAxZPEC&printsec=frontcover&img=1&zoom=5'",
            "quantity": 13,
            "price": 639,
            "description": "The final installment in the epic series completes the quest of Roland Deschainwho works to outmaneuver the increasingly desperate acts of his adversaries and confronts losses within his circle of companions.'"
        }
        self.create_products_invalid_payload = {
            "author": "Stephen King'",
            "title": "The Dark Tower VII'",
            "image": "http://books.google.com/books/content?id=Geq0uKAxZPEC&printsec=frontcover&img=1&zoom=5'",
            "price": 639,

        }
        self.update_products_payload = {
            "author": "Stephen Queen'",
            "title": "The Dark Tower VIII'",
            "image": "http://books.google.com/books/content?id=Geq0uKAxZPEC&printsec=frontcover&img=1&zoom=5'",
            "quantity": 20,
            "price": 650,
            "description": "The final installment in the epic series completes the quest of Roland Deschainwho works to outmaneuver the increasingly desperate acts of his adversaries and confronts losses within his circle of companions.'"
        }
        self.login = {
            "username": "sankeyyy22", "password": "sanket000002"
        }

    def test_create_products_with_valid_payload(self):
        response = self.client.post(reverse('create'), data=json.dumps(self.create_products_valid_payload),
                                    content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_products_with_invalid_payload(self):
        response = self.client.post(reverse('create'), data=json.dumps(self.create_products_invalid_payload),
                                    content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_products(self):
        response = self.client.get(reverse('create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product_with_valid_product_id(self):
        response = self.client.put(reverse('product-operation', kwargs={'id': 7}),
                                   data=json.dumps(self.update_products_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product_with_invalid_product_id(self):
        response = self.client.put(reverse('product-operation', kwargs={'id': 60}),
                                   data=json.dumps(self.update_products_payload), content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_with_valid_product_id(self):
        response = self.client.delete(reverse('product-operation', kwargs={'id': 52}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product_with_invalid_product_id(self):
        response = self.client.delete(reverse('product-operation', kwargs={'id': 60}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_notes(self):
        client = APIClient()
        response = client.get('api/books/search/The')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_cart_valid_payload(self):
        client = APIClient()
        token = self.get_token('sanket', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/cart/7')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_cart_invalid_payload(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/cart/7')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_place_order_api_valid_palyload(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/place-order/', {
            "address": "176,Rohini Nagar-3,Jule Solapur,Solapur",
            "phone": "9422484996"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_place_order_api_invalid_credentials(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket111', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/place-order/', {
            "address": "176,Rohini Nagar-3,Jule Solapur,Solapur",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_place_order_api_invalid_payload(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/place-order/', {
            "address": "176,Rohini Nagar-3,Jule Solapur,Solapur",
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_to_wish_list_valid_payload(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/wish/7')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_wish_list_invalid_credentials(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket112', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/wish/7')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_to_wish_list_invalid_payload(self):
        client = APIClient()
        # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InNhbmtleXl5MjIifQ.U1pm5GpM0GteJdlHUFMXVYYpTJNIjv6pXWwU_hXQP0A"
        token = self.get_token('sanket', 'sanket0002')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.post('api/books/wish/70')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def get_token(self, username, password):
        user = User.objects.get(username=username, password=password)
        if user:
            auth_token = jwt.encode(
                {'username': user.username}, settings.SECRET_KEY, algorithm='HS256')

            # serializer = UserSerializer(user)

            # data = {'user': serializer.data, 'token': auth_token}

            return auth_token
