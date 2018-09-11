import unittest
from django.test import Client

# Create your tests here.


class LoginTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def simple_login_test(self):
        # Issue a GET request.
        response = self.client.post('/admin/login', {'username': 'admin', 'password': '123456'}, follow=True)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 5 customers.
        #self.assertEqual(len(response.context['customers']), 5)