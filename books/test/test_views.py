from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json
from rest_framework.test import APITestCase

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

        self.search_products_valid_payload = {
            "value": "The"
        }

        self.search_products_invalid_payload = {
            "key": "The"
        }
        self.valid_login_credentials = {
            "username": "sanket12345", "password": "sanket00002", "email": "ss@gmail.com", "phone": "8888881800"
        }
        self.invalid_login_credentials = {
            "username": "sanke", "password": "sanket000002", "email": "ssssdv@gmail.com", "phone": "8888881800"
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

    def test_get_all_products_from_high_to_low_price(self):
        response = self.client.get(reverse('order-high'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_products_from_low_to_high_price(self):
        response = self.client.get(reverse('order-low'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_notes_valid_payload(self):
        response = self.client.get(reverse('search'), data=json.dumps(self.search_products_valid_payload),
                                   content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_notes_invalid_payload(self):
        response = self.client.post(reverse('search'), data=json.dumps(self.search_products_invalid_payload),
                                    content_type=CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def login_method(self, credentials):
        login = self.client.post(reverse('login'), data=json.dumps(credentials), content_type=CONTENT_TYPE)
        token = login.get('Authorization')
        auth_headers = {
            'HTTP_AUTHORIZATION': token,
        }
        return auth_headers

    # Not Working
    def test_add_to_cart_valid_payload(self):
        auth_headers = self.login_method(self.valid_login_credentials)
        response = self.client.post(reverse('cart'), **auth_headers, kwargs={'id': 22})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Not Working
    def test_add_to_cart_invalid_payload(self):
        auth_headers = self.login_method(self.invalid_login_credentials)
        response = self.client.post(reverse('cart'), **auth_headers, kwargs={'id': 22})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
