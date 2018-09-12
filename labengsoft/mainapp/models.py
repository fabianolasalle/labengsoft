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
    """
    Ambiente de configuração do SIGEP
    
    Usuário -- Usuário do SIGEPMaster
    Senha -- Senha do SIGEPMaster
    CNPJ -- CNPJ do cliente
    nomeEmpresa -- Nome da empresa cliente
    ativo -- Flag que sinaliza se o ambiente está ativo ou não ()
    """
    usuario = models.CharField(max_length=50, blank=False, null=False)
    senha = models.CharField(max_length=50, blank=False, null=False)
    cnpj = models.CharField(max_length=14, blank=False, null=False)
    nomeEmpresa = models.CharField(max_length=50, blank=False, null=False)
    ambiente = models.CharField(max_length=20, blank=False, null=False)
    ativo = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario + " - " + self.ambiente


class Servico(models.Model):
    """
    Model de serviços disponíveis, preenchido conforme serviços disponíveis
    ao cartão do cliente.

    idServico -- identificador de serviço dos Correios
    codigo -- Código de serviço correspondente
    descr -- Descrição do serviço
    """
    idServico = models.IntegerField(blank=False, null=False)
    codigo = models.IntegerField(blank=False, null=False)
    descr = models.CharField(max_length=100, blank=False, null=False)
    
    def __str__(self):
        return self.descr
 

class CartaoPostagem(models.Model):
    """
    Model de cartão de postagem

    nroCartao -- Número do cartão
    nroContrato -- Número do contrato do cliente
    codAdmin -- Código administrativo
    servicos -- Serviços disponíveis para este cartão
    ativo -- Flag que indica se o cartão está ativo ou não (opcional)
    vencimento -- Vencimento do cartão de postagem
    codDR -- Código do diretório regional do cartão
    """
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
        """
        Filtra nos contratos do usuário o contrato e o cartão correspondentes.
        Retorna uma lista contendo, respectivamente, o contrato e cartão encontrados.

        contratos -- Lista de contratos do cliente com os Correios
        nroContrato -- Número do contrato a ser encontrado
        nroCartao -- Número do cartão a ser encontrado

        """
        contrato = list(filter(lambda c: c.number == int(nroContrato), contratos))
        cartao = list(filter(lambda c: c.number == nroCartao, contrato[0].posting_cards))
        return [contrato[0], cartao[0]]

    def updateCartaoServicosAndDR(self):
        """ Atualiza a tabela de serviços disponíveis ao cliente pelo cartão, bem como preenche o diretório regional. """
        # Conexão com o webservice
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)

        # Consulta o usuário e filtra o contrato e cartão desejados
        user = cliente.get_user (self.nroContrato, self.nroCartao)
        contrato, cartao = CartaoPostagem._getContratoAndCartao(user.contracts, self.nroContrato, self.nroCartao)

        # Atualiza a tabela de serviços
        for s in cartao.services:
            self.servicos.create (idServico=s.id, codigo=s.code, descr=s.display_name)
        
        # Preenche o código do diretório regional
        self.codDR = contrato.regional_direction.number

    def getCartaoStatus(self):
        """ Pesquisa no servidor dos Correios o status do cartão e sua data de vencimento. """
        # Conexão com o webservice
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)

        # Consulta e preenche o status
        status = cliente._auth_call('getStatusCartaoPostagem', self.nroCartao)
        if status == 'Normal':
            self.ativo = True
        elif status == 'Cancelado':
            self.ativo == False

        # Pesquisa a data de vencimento do cartão de postagem
        user = cliente.get_user (self.nroContrato, self.nroCartao)
        contrato, cartao = CartaoPostagem._getContratoAndCartao(user.contracts, self.nroContrato, self.nroCartao)
        self.vencimento = contrato.end_date
        

class Endereco(models.Model):
    """
    Model de endereço

    cep -- CEP do logradouro
    logradouro -- Tipo e nome do logradouro
    numero -- Número do endereço
    complemento -- Complemento do endereço (sala, apto., etc...) (opcional)
    bairro -- Bairro do endereço
    cidade -- Cidade do logradouro
    uf -- Sigla do estado (Unidade federativa)
    default -- Endereço padrão
    """
    cep = models.CharField(max_length=10, blank=False, null=False)
    logradouro = models.CharField(max_length=100, blank=False, null=False)
    numero = models.CharField(max_length=5, blank=False, null=False)
    complemento = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=30, blank=False, null=False)
    cidade = models.CharField(max_length=30, blank=False, null=False)
    uf = models.CharField(max_length=2, blank=False, null=False)
    default = models.BooleanField(default=False)

    def getEnderecoByCep(self):
        """ Preenche os dados de endereço com base na pesquisa por CEP dos Correios."""
        # Conexão com o webservice
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
        
        # Pesquisa por CEP e preenchimento dos demais dados
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
    """
    Model de grupo de destinatários

    nome -- Nome do grupo
    descr -- Descrição do grupo
    """
    nome = models.CharField(max_length=30, blank=False, null=False)
    descr = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.nome 

class Telefone(models.Model):
    """
    Model para cadastro de telefones dos contatos

    numero -- Número de telefone com DDD
    tipo -- Tipo de telefone. Fixo = 1, Celular = 2, Fax = 3 (padrão 1)
    default -- Telefone padrão
    """
    numero = models.CharField(max_length=15, blank=False, null=False)
    tipo = models.IntegerField(default=1, blank=False, null=False)
    default = models.BooleanField(default=False, blank=False, null=False)
    
    def __str__(self):
        return 


class Destinatario(models.Model):
    """
    Model de destinatário

    nome -- Nome do destinatário
    cpfCnpj -- CPF ou CNPJ do destinatário
    telefones -- Telefones do destinatário
    email -- E-mail do destinatário (opcional)
    enderecos -- Endereços do destinatário
    """
    nome = models.CharField(max_length=50, blank=False, null=False)
    cpfCnpj = models.CharField(max_length=14, blank=False, null=False)
    telefones = models.ForeignKey(Telefone, on_delete=models.PROTECT)
    email = models.CharField(max_length=50, blank=True, null=True)
    enderecos = models.ManyToManyField(Endereco)

    def __str__(self):
        return self.nome


class Remetente(models.Model):
    """
    Model de remetente

    nome -- Nome do remetente
    cpfCnpj -- CPF ou CNPJ do remetente
    telefones -- Telefones do remetente
    email -- E-mail do remetente (opcional)
    enderecos -- Endereços do remetente
    cartaoPostagem -- Cartões de postagem do remetente
    """
    nome = models.CharField(max_length=50, blank=False, null=False)
    cpfCnpj = models.CharField(max_length=14, blank=False, null=False)
    telefones = models.ForeignKey(Telefone, on_delete=models.PROTECT)
    email = models.CharField(max_length=50, blank=True, null=True)
    enderecos = models.ManyToManyField(Endereco)
    cartaoPostagem = models.ManyToManyField(CartaoPostagem)

    def __str__(self):
        return self.nome

    
class Embalagem(models.Model):
    """
    Model de embalagem

    descr -- Descrição da embalagem (opcional)
    peso -- Peso em gramas (opcional, padrão=0)
    ativo -- Pacote está ativo ou não (opcional)
    tipo -- ID do tipo de pacote (Pacote ou caixa=1, Cilindro ou esféra=2) (padrão=1)
    comprimento -- Comprimento do pacote (padrão=0)
    largura -- Largura do pacote (padrão=0)
    altura -- Altura do pacote (padrão=0)
    diametro -- Diâmetro do pacote (caso seja redondo) (padrão=0)
    obs -- Observações sobre o pacote (opcional)
    """
    descr = models.CharField(max_length=50, blank=True, null=True)
    peso = models.FloatField(default=0.0)
    ativo = models.BooleanField (blank=True, null=True)
    tipo = models.PositiveIntegerField (default=1, blank=True, null=True)
    comprimento = models.FloatField (default=0.0, blank=False, null=False)
    largura = models.FloatField(default=0.0, blank=False, null=False)
    altura = models.FloatField(default=0.0, blank=False, null=False)
    diametro = models.FloatField(default=0.0, blank=False, null=False)
    obs = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.descr

# TODO: Serviços extras (provavelmente terá que criar mais um model)
class ObjetoPostal(models.Model):
    """
    Model do objeto postal

    destinatario -- Destinatário final do objeto
    endSelecionado -- Endereço selecionado do destinatário
    servico -- Serviço a ser utilizado
    codRastreamento -- Código de rastreamento do objeto
    descr -- Descrição do objeto postal
    embalagem -- Tipo de embalagem do objeto
    qtdObj -- Quantidade de objetos (opcional)
    nf -- Número da nota fiscal (opcional)
    nroPedido -- Número do pedido (opcional)
    obs -- Observações (opcional)
    """
    destinatario = models.ManyToManyField(Destinatario)
    endSelecionado = models.OneToOneField(Endereco, on_delete=models.PROTECT)
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    codRastreamento = models.CharField(max_length=100, blank=False, null=False)
    descr = models.CharField(max_length=50, blank=False, null=False)
    embalagem = models.OneToOneField(Embalagem, on_delete=models.PROTECT, blank=True, null=True)
    qtdObj = models.PositiveIntegerField(blank=True, null=True)
    nf = models.CharField(max_length=20, blank=True, null=True)
    nroPedido = models.CharField(max_length=20, blank=True, null=True)
    obs = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.codRastreamento
    
    def getCodRastreamento (self):
        """ Adquire o código de rastreamento do objeto """
        # Conexão com o webservice
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)

        # Solicita ao SIGEP o código de rastreamento.
        user = User (env.nomeEmpresa, env.cnpj)
        service = Service.get(self.servico.codigo)
        self.codRastreamento = cliente.request_tracking_codes(user, service, 1)[0].code

    def selecionaEndereco (self, idEnd):
        """ Seleciona o endereço de destino do objeto postal """
        if idEnd:
            self.endSelecionado = self.destinatario.enderecos.get(id=idEnd)
        else:
            self.endSelecionado = self.destinatario.enderecos.get(default=True)

    def converteEnderecoSelecionado (self):
        """ 
        Converte o objeto do model Endereco em um objeto Address compatível com a biblioteca
        do webservice.
        """
        addr = Address(name=self.destinatario.nome, street=self.endSelecionado.logradouro, number=self.endSelecionado.numero, complement=self.endSelecionado.complemento, neighborhood=self.endSelecionado.bairro, city=self.endSelecionado.cidade, state=self.endSelecionado.uf, zip_code=self.endSelecionado.cep)
        return addr
        
class PreListaPostagem(models.Model):
    """
    Model de pré-lista de postagem

    remetente -- Remetente
    endSelecionado -- Endereço selecionado do remetente
    cartaoPostagem -- Cartão de postagem do remetente
    objetosPostais -- Objetos a serem enviados
    fechada -- Status da lista de postagem (fechada ou aberta)
    dataCriacao -- Data de criação da lista de postagem
    qtdObjetos -- Quantidade de objetos postais
    """
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
        """ 
        Converte o objeto do model Endereco em um objeto Address compatível com a biblioteca
        do webservice.
        """
        addr = Address(name=self.remetente.nome, street=self.endSelecionado.logradouro, number=self.endSelecionado.numero, complement=self.endSelecionado.complemento, neighborhood=self.endSelecionado.bairro, city=self.endSelecionado.cidade, state=self.endSelecionado.uf, zip_code=self.endSelecionado.cep)
        return addr

    def fecharPLP (self):
        """ Fecha a PLP e a envia para o servidor, tornando-a uma lista de postagem """
        # Conexão com o webservice
        env = SigepEnvironment.objects.get(ativo=True)
        cliente = correios.Correios(username=env.usuario, password=env.senha, environment=env.ambiente)
<<<<<<< HEAD

        # Cria os objetos necessários para o fechamento da PLP
        cartao = CartaoPostagem.objects.get(ativo=True)
        user = User(env.nomeEmpresa, env.cnpj)
        contract = Contract(user, cartao.nroContrato, cartao.codDR)
        postingCard = PostingCard(contract, cartao.nroCartao, cartao.codAdmin)
        senderAddr = self.converteEnderecoSelecionado()

        # Inicialização da PLP
        plp = PostingList(self.id)
        
        # Inclusão dos objetos postais 
        for op in self.objetosPostais.all():
            sl = ShippingLabel(postingCard, senderAddr, op.converteEnderecoSelecionado(), Servico.objects.first().codigo, op.codRastreamento, 1)
            sl.posting_card = postingCard
            plp.add_shipping_label(sl)
        
        # Fechamento da PLP.
        plp = cliente.close_posting_list(plp,cartao.nroCartao)
=======
>>>>>>> 0af253d725bcda280294c833bca9e0caadef5b18
