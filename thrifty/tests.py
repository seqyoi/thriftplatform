from django.test import TestCase

# Create your tests here.
from thrifty.models import Product, Profile
from django.contrib.auth.models import User

class ProductTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", description="This is a test product.", price=9.99)
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "This is a test product.")
        self.assertEqual(self.product.price, 9.99)

class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
    def test_user_authentication(self):
        login_successful = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login_successful)

from django.urls import reverse 