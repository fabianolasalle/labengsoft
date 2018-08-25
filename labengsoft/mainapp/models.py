from django.db import models

# Create your models here.

class Pessoa(models.Model):
    nome = models.CharField(max_length=60)
    cpf_cpnj = models.CharField(max_length=14)
    telefone = models.CharField(max_length=11)

    def __str__(self):
        return self.nome