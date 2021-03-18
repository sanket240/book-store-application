from django.test import TestCase
from books.models import Products


class ProductTest(TestCase):

    def setUp(self):
        Products.objects.create(author='Robert K', title='Rich Dad Poor Dad', image="http://books.google.com/books"
                                                                                    "/content?id=FNn5DQAAQBAJ"
                                                                                    "&printsec=frontcover&img=1&zoom"
                                                                                    "=5'",
                                quantity=14, price=645, description="Newly introduced by the author--Cover")

    def test_create_note(self):
        product = Products.objects.get(title='Rich Dad Poor Dad')
        self.assertEqual(product.get_title(), "Rich Dad Poor Dad")



