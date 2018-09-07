from django.db import models

from correios.exceptions import (
    AuthenticationError,
    CanceledPostingCardError,
    ClosePostingListError,
    ConnectTimeoutError,
    NonexistentPostingCardError,
    PostingListSerializerError,
    TrackingCodesLimitExceededError,
)
from correios.models.address import ZipCode
from correios.models.builders import ModelBuilder
from correios.models.data import (
    EXTRA_SERVICE_AR,
    EXTRA_SERVICE_MP,
    EXTRA_SERVICE_VD,
    FREIGHT_ERROR_FINAL_ZIPCODE_RESTRICTED,
    FREIGHT_ERROR_INITIAL_AND_FINAL_ZIPCODE_RESTRICTED,
    FREIGHT_ERROR_INITIAL_ZIPCODE_RESTRICTED,
    SERVICE_PAC,
    SERVICE_SEDEX,
    SERVICE_SEDEX10,
)
from correios.models.posting import (
    FreightResponse,
    NotFoundTrackingEvent,
    PostalUnit,
    PostInfo,
    PostingList,
    TrackingCode,
)
from correios.models.user import ExtraService, PostingCard, Service
from correios.serializers import PostingListSerializer
from correios.utils import get_resource_path, to_decimal
from correios.xml_utils import fromstring
from correios import client as correios

# Create your models here.

class SigepEnvironment(models.Model):
    
    usuario = models.CharField(max_length=50, blank=False, null=False)
    senha = models.CharField(max_length=50, blank=False, null=False)
    ambiente = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.usuario + " - " + self.ambiente


class Servico(models.Model):

    codigo = models.IntegerField(primary_key=True, blank=False, null=False)
    descr = models.CharField(max_length=100, blank=False, null=False)
    
    def __str__(self):
        return self.descr
 

class CartaoPostagem(models.Model):
    
    nroCartao = models.CharField(max_length=10, blank=False, null=False)
    nroContrato = models.CharField(max_length=10, blank=False, null=False)
    servicos = models.ManyToManyField(Servico)
    ativo = models.BooleanField(default=True)
    vencimento = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)

    def __str__(self):
        return self.nroCartao

    @staticmethod
    def _getContratoAndCartao(contratos, nroContrato, nroCartao):
        contrato = list(filter(lambda c: c.number == int(nroContrato), contratos))
        cartao = list(filter(lambda c: c.number == nroCartao, contrato[0].posting_cards))
        return [contrato[0], cartao[0]]

    def updateCartaoServicos(self):
        env = SigepEnvironment.objects.first()
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        user = cliente.get_user (self.nroContrato, self.nroCartao)
        contrato, cartao = CartaoPostagem._getContratoAndCartao(user.contracts, self.nroContrato, self.nroCartao)
        
        for s in cartao.services:
            self.servicos.create (codigo=s.code, descr=s.display_name)

    def getCartaoStatus(self):
        env = SigepEnvironment.objects.first()
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        status = cliente._auth_call('getStatusCartaoPostagem', self.nroCartao)
        if status == 'Normal':
            self.ativo = True
        elif status == 'Cancelado':
            self.ativo == False

        user = cliente.get_user (self.nroContrato, self.nroCartao)
        contrato, cartao = CartaoPostagem._getContratoAndCartao(user.contracts, self.nroContrato, self.nroCartao)
        self.vencimento = contrato.end_date
        

class Endereco(models.Model):
    
    cep = models.CharField(max_length=10, blank=False, null=False)
    logradouro = models.CharField(max_length=100, blank=False, null=False)
    numero = models.CharField(max_length=5, blank=False, null=False)
    complemento = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=30, blank=False, null=False)
    cidade = models.CharField(max_length=30, blank=False, null=False)
    uf = models.CharField(max_length=2, blank=False, null=False)
    default = models.BooleanField(default=False)

    def getEnderecoByCep(self):
        env = SigepEnvironment.objects.first()
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        zip = cliente.find_zipcode(ZipCode(self.cep))
        self.logradouro = zip.address
        self.bairro = zip.district
        self.cidade = zip.city
        self.uf = zip.state.code

    #def __str__(self):
    #    return 

    #def __unicode__(self):
    #    return 

class GrupoDestinatario(models.Model):
    
    nome = models.CharField(max_length=30, blank=False, null=False)
    descr = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.nome 

class Telefone(models.Model):
    
    numero = models.CharField(max_length=15, blank=False, null=False)
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return 


class Destinatario(models.Model):
    
    nome = models.CharField(max_length=50, blank=False, null=False)
    cpfCnpj = models.CharField(max_length=30, blank=False, null=False)
    telefones = models.ForeignKey(Telefone, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, blank=True, null=True)
    enderecos = models.ManyToManyField(Endereco)

    def __str__(self):
        return self.nome


class Remetente(models.Model):
    
    nome = models.CharField(max_length=50, blank=False, null=False)
    cpfCnpj = models.CharField(max_length=30, blank=False, null=False)
    telefones = models.ForeignKey(Telefone, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, blank=True, null=True)
    enderecos = models.ManyToManyField(Endereco)
    cartaoPostagem = models.ManyToManyField(CartaoPostagem)

    def __str__(self):
        return self.nome

    
class Embalagem(models.Model):

    descr = models.CharField(max_length=50, blank=False, null=False)
    peso = models.PositiveIntegerField (blank=False, null=False)
    ativo = models.BooleanField (default=False)
    tipo = models.PositiveIntegerField (blank=False, null=False)
    comprimento = models.PositiveIntegerField(blank=False, null=False)
    largura = models.PositiveIntegerField(blank=False, null=False)
    altura = models.PositiveIntegerField(blank=False, null=False)
    obs = models.CharField(max_length=300, blank=False, null=True)

    def __str__(self):
        return 

# TODO
class ObjetoPostal(models.Model):


    def __str__(self):
        return 

    def __unicode__(self):
        return 
# TODO
class PreListaPostagem(models.Model):
    
    def __str__(self):
        return 

    def __unicode__(self):
        return 
