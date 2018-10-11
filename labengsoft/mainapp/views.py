from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import *
from django.core import serializers
from .models import *
from django.urls import reverse_lazy
import json

# Create your views here.
# ========================================
# Views do CRUD de endereços
# ========================================

class EnderecoCreateView(CreateView):
    model = Endereco
    fields = '__all__'
    success_url = reverse_lazy('enderecos-main')

class EnderecoUpdateView(UpdateView):
    model = Endereco
    fields = '__all__'
    success_url = reverse_lazy('enderecos-main')

class EnderecoDeleteView (DeleteView):
    model = Endereco
    success_url = reverse_lazy('enderecos-main')

class EnderecoDetailView(DetailView):
    model = Endereco
    context_object_name = 'endereco'

class EnderecosView (ListView):
    model = Endereco

#def index(request):
#    return HttpResponse("Hello, world. Index!")
def enderecoByCepView (request, cep):
    try:
        endereco = serializers.serialize ('json', [ Endereco.getEnderecoByCep(str(cep)) ])
        return JsonResponse(endereco, safe=False)
    except Exception as ex:
        print (cep)
        raise

# ========================================


# ========================================
# Views do CRUD de destinatário
# ========================================

class DestinatarioCreateView(CreateView):
    model = Destinatario
    fields = '__all__'
    success_url = reverse_lazy('destinatarios-main')

class DestinatarioUpdateView(UpdateView):
    model = Destinatario
    fields = '__all__'
    success_url = reverse_lazy('destinatarios-main')

class DestinatarioDeleteView (DeleteView):
    model = Destinatario
    success_url = reverse_lazy('destinatarios-main')

class DestinatarioDetailView(DetailView):
    model = Destinatario
    context_object_name = 'destinatario'

class DestinatariosView (ListView):
    model = Destinatario

# ========================================


# ========================================
# Views do CRUD de Telefone
# ========================================

class TelefoneCreateView(CreateView):
    model = Telefone
    fields = '__all__'
    success_url = reverse_lazy('telefones-main')

class TelefoneUpdateView(UpdateView):
    model = Telefone
    fields = '__all__'
    success_url = reverse_lazy('telefones-main')

class TelefoneDeleteView (DeleteView):
    model = Telefone
    success_url = reverse_lazy('telefones-main')

class TelefoneDetailView(DetailView):
    model = Telefone
    context_object_name = 'telefone'

class TelefonesView (ListView):
    model = Telefone

# ========================================


# ========================================
# Views do CRUD de Grupo de Destinatários
# ========================================

class GrupoDestCreateView(CreateView):
    model = GrupoDestinatario
    fields = '__all__'
    success_url = reverse_lazy('grupodest-main')

class GrupoDestUpdateView(UpdateView):
    model = GrupoDestinatario
    fields = '__all__'
    success_url = reverse_lazy('grupodest-main')

class GrupoDestDeleteView (DeleteView):
    model = GrupoDestinatario
    success_url = reverse_lazy('grupodest-main')

class GrupoDestDetailView(DetailView):
    model = GrupoDestinatario
    context_object_name = 'grupodest'

class GruposDestView (ListView):
    model = GrupoDestinatario

# ========================================


# ========================================
# Views do CRUD de Embalagem
# ========================================

class EmbalagemCreateView(CreateView):
    model = Embalagem
    fields = '__all__'
    success_url = reverse_lazy('embalagem-main')

class EmbalagemUpdateView(UpdateView):
    model = Embalagem
    fields = '__all__'
    success_url = reverse_lazy('embalagem-main')

class EmbalagemDeleteView (DeleteView):
    model = Embalagem
    success_url = reverse_lazy('embalagem-main')

class EmbalagemDetailView(DetailView):
    model = Embalagem
    context_object_name = 'embalagem'

class EmbalagensView (ListView):
    model = Telefone

# ========================================



# ========================================
# Views do CRUD de Objetos postais
# ========================================

class ObjPostalCreateView(CreateView):
    model = ObjetoPostal
    fields = '__all__'
    success_url = reverse_lazy('objpostal-main')

class ObjPostalUpdateView(UpdateView):
    model = ObjetoPostal
    fields = '__all__'
    success_url = reverse_lazy('objpostal-main')

class ObjPostalDeleteView (DeleteView):
    model = ObjetoPostal
    success_url = reverse_lazy('objpostal-main')

class ObjPostalDetailView(DetailView):
    model = ObjetoPostal
    context_object_name = 'objpostal'

class ObjPostalView (ListView):
    model = ObjetoPostal

# ========================================