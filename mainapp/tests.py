import unittest
from django.test import Client

class LoginTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_login(self):
        # Issue a GET request.
        response = self.client.post('/admin', {'username': 'admin', 'password' : 'admin'}, follow=True)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)


        # Check that the rendered context contains 5 customers.
        #self.assertEqual(len(response.context['customers']), 5)

    def test_access_list(self):
        response = self.client.post('/admin', {'username': 'admin', 'password': 'admin'}, follow=True)
        self.assertEqual(response.status_code, 200)

        urls = [
            '/admin/mainapp/cartaopostagem/',
            '/admin/mainapp/destinatario/',
            '/admin/mainapp/embalagem/',
            '/admin/mainapp/endereco/',
            '/admin/mainapp/grupodestinatario/',
            '/admin/mainapp/objetopostal/',
            '/admin/mainapp/prelistapostagem/',
            '/admin/mainapp/remetente/',
            '/admin/mainapp/servico/',
            '/admin/mainapp/sigepenvironment/',
            '/admin/mainapp/telefone/'
        ]

        for url in urls:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_access_add(self):
        response = self.client.post('/admin', {'username': 'admin', 'password': 'admin'}, follow=True)
        self.assertEqual(response.status_code, 200)

        urls = ['/admin/mainapp/cartaopostagem/add/',
            '/admin/mainapp/destinatario/add/',
            '/admin/mainapp/embalagem/add/',
            '/admin/mainapp/grupodestinatario/add/',
            '/admin/mainapp/objetopostal/add/',
            '/admin/mainapp/prelistapostagem/add/',
            '/admin/mainapp/remetente/add/',
            '/admin/mainapp/servico/add/',
            '/admin/mainapp/sigepenvironment/add/',
            '/admin/mainapp/telefone/add/'
        ]

        for url in urls:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)