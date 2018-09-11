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
    ShippingLabel,
)
from correios.models.user import ExtraService, PostingCard, Service, User, Contract
from correios.models.address import Address
from correios.serializers import PostingListSerializer
from correios.utils import get_resource_path, to_decimal
from correios.xml_utils import fromstring
from correios import client as correios

# Create your models here.

class SigepEnvironment(models.Model):
    
    usuario = models.CharField(max_length=50, blank=False, null=False)
    senha = models.CharField(max_length=50, blank=False, null=False)
    cnpj = models.CharField(max_length=14, blank=False, null=False)
    nomeEmpresa = models.CharField(max_length=50, blank=False, null=False)
    ambiente = models.CharField(max_length=20, blank=False, null=False)
    ativo = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario + " - " + self.ambiente


class Servico(models.Model):

    idServico = models.IntegerField(blank=False, null=False)
    codigo = models.IntegerField(blank=False, null=False)
    descr = models.CharField(max_length=100, blank=False, null=False)
    
    def __str__(self):
        return self.descr
 

class CartaoPostagem(models.Model):
    
    nroCartao = models.CharField(max_length=10, blank=False, null=False)
    nroContrato = models.CharField(max_length=10, blank=False, null=False)
    codAdmin = models.CharField(max_length=8, blank=False, null=False)
    servicos = models.ManyToManyField(Servico)
    ativo = models.BooleanField(default=True)
    vencimento = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    codDR = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.nroCartao

    @staticmethod
    def _getContratoAndCartao(contratos, nroContrato, nroCartao):
        contrato = list(filter(lambda c: c.number == int(nroContrato), contratos))
        cartao = list(filter(lambda c: c.number == nroCartao, contrato[0].posting_cards))
        return [contrato[0], cartao[0]]

    def updateCartaoServicosAndDR(self):
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        user = cliente.get_user (self.nroContrato, self.nroCartao)
        contrato, cartao = CartaoPostagem._getContratoAndCartao(user.contracts, self.nroContrato, self.nroCartao)

        for s in cartao.services:
            self.servicos.create (idServico=s.id, codigo=s.code, descr=s.display_name)
        self.codDR = contrato.regional_direction.number

    def getCartaoStatus(self):
        env = SigepEnvironment.objects.get(ativo=True)
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
        env = SigepEnvironment.objects.get(ativo=True)
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
    tipo = models.IntegerField(default=1, blank=False, null=False)
    default = models.BooleanField(default=False, blank=False, null=False)
    
    def __str__(self):
        return 


class Destinatario(models.Model):
    
    nome = models.CharField(max_length=50, blank=False, null=False)
    cpfCnpj = models.CharField(max_length=14, blank=False, null=False)
    telefones = models.ForeignKey(Telefone, on_delete=models.PROTECT)
    email = models.CharField(max_length=50, blank=True, null=True)
    enderecos = models.ManyToManyField(Endereco)

    def __str__(self):
        return self.nome


class Remetente(models.Model):
    
    nome = models.CharField(max_length=50, blank=False, null=False)
    cpfCnpj = models.CharField(max_length=14, blank=False, null=False)
    telefones = models.ForeignKey(Telefone, on_delete=models.PROTECT)
    email = models.CharField(max_length=50, blank=True, null=True)
    enderecos = models.ManyToManyField(Endereco)
    cartaoPostagem = models.ManyToManyField(CartaoPostagem)

    def __str__(self):
        return self.nome

    
class Embalagem(models.Model):

    descr = models.CharField(max_length=50, blank=False, null=False)
    peso = models.FloatField(default=0.0)
    ativo = models.BooleanField (default=False, blank=False, null=False)
    tipo = models.PositiveIntegerField (blank=False, null=False)
    comprimento = models.FloatField (default=0.0, blank=False, null=False)
    largura = models.FloatField(default=0.0, blank=False, null=False)
    altura = models.FloatField(default=0.0, blank=False, null=False)
    diametro = models.FloatField(default=0.0, blank=False, null=False)
    obs = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.descr

# TODO: Serviços extras (provavelmente terá que criar mais um model)
class ObjetoPostal(models.Model):
    destinatario = models.ManyToManyField(Destinatario)
    endSelecionado = models.OneToOneField(Endereco, on_delete=models.PROTECT)
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    codRastreamento = models.CharField(max_length=100, blank=False, null=False)
    descr = models.CharField(max_length=50, blank=False, null=False)
    embalagem = models.OneToOneField(Embalagem, on_delete=models.PROTECT, blank=True, null=True)
    qtdObj = models.PositiveIntegerField(blank=True, null=True)
    peso = models.PositiveIntegerField (blank=False, null=False)
    tipo = models.PositiveIntegerField (blank=False, null=False)
    comprimento = models.FloatField (default=0.0, blank=False, null=False)
    largura = models.FloatField(default=0.0, blank=False, null=False)
    altura = models.FloatField(default=0.0, blank=False, null=False)
    diametro = models.FloatField(default=0.0, blank=False, null=False)
    nf = models.CharField(max_length=20, blank=True, null=True)
    nroPedido = models.CharField(max_length=20, blank=True, null=True)
    obs = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.codRastreamento
    
    def getCodRastreamento (self):
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        user = User (env.nomeEmpresa, env.cnpj)
        service = Service.get(self.servicos.codigo)
        self.codRastreamento = cliente.request_tracking_codes(user, service, 1)[0].code

    def selecionaEndereco (self, idEnd):
        if idEnd:
            self.endSelecionado = self.destinatario.enderecos.get(id=idEnd)
        else:
            self.endSelecionado = self.destinatario.enderecos.get(default=True)

    def converteEnderecoSelecionado (self):
        addr = Address(name=self.destinatario.nome, street=self.endSelecionado.logradouro, number=self.endSelecionado.numero, complement=self.endSelecionado.complemento, neighborhood=self.endSelecionado.bairro, city=self.endSelecionado.cidade, state=self.endSelecionado.uf, zip_code=self.endSelecionado.cep)
        return addr
        
class PreListaPostagem(models.Model):
    remetente = models.OneToOneField(Remetente, on_delete=models.PROTECT)
    endSelecionado = models.OneToOneField(Endereco, on_delete=models.PROTECT)
    cartaoPostagem = models.OneToOneField(CartaoPostagem, on_delete=models.PROTECT)
    objetosPostais = models.ForeignKey(ObjetoPostal, on_delete=models.PROTECT)
    fechada = models.BooleanField(default=False)
    dataCriacao = models.DateField(auto_now=True, blank=False, null=False)
    qtdObjetos = models.PositiveIntegerField(blank=False, null=False)

    def __str__(self):
        return self.id

    def selecionaEndereco (self, idEnd):
        if idEnd:
            self.endSelecionado = self.remetente.enderecos.get(id=idEnd)
        else:
            self.endSelecionado = self.remetente.enderecos.get(default=True)

    def converteEnderecoSelecionado (self):
        addr = Address(name=self.remetente.nome, street=self.endSelecionado.logradouro, number=self.endSelecionado.numero, complement=self.endSelecionado.complemento, neighborhood=self.endSelecionado.bairro, city=self.endSelecionado.cidade, state=self.endSelecionado.uf, zip_code=self.endSelecionado.cep)
        return addr

    def fecharPLP (self):
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        cartao = CartaoPostagem.objects.get(ativo=True)
        user = User(env.nomeEmpresa, env.cnpj)
        contract = Contract(user, cartao.nroContrato, cartao.codDR)
        postingCard = PostingCard(contract, cartao.nroCartao, cartao.codAdmin)
        senderAddr = self.converteEnderecoSelecionado()
        plp = PostingList(self.id)

        for op in self.objetosPostais.all():
            sl = ShippingLabel(postingCard, senderAddr, op.converteEnderecoSelecionado(), Servico.objects.first().codigo, op.codRastreamento, 1)
            sl.posting_card = postingCard
            plp.add_shipping_label(sl)
        plp = cliente.close_posting_list(plp,cartao.nroCartao)