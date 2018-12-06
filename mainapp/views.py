from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import *
from django.core import serializers
from .models import *
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from .forms import *
from django.contrib.messages.views import SuccessMessageMixin
from bootstrap_modal_forms.mixins import PassRequestMixin

import json

# ========================================
# View da página principal
# ========================================

class MainView(View):
    def get(self, request, *args, **kwargs):
        return render (request, 'mainapp/main.html')

    def post(self, request, *args, **kwargs):
        return render (request, 'mainapp/main.html')

# ========================================



# ========================================
# Views do CRUD de endereços
# ========================================

class EnderecoCreateView(CreateView, SuccessMessageMixin):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço criado com sucesso'
    #success_url = reverse_lazy (request.GET['origin'])

class EnderecoUpdateView(UpdateView):
    model = Endereco
    fields = '__all__'
    success_message = 'Endereço atualizado com sucesso'
    #success_url = reverse_lazy (request.GET['origin'])

class EnderecoDeleteView (DeleteView):

    model = Endereco
    success_message = 'Endereço excluído com sucesso'
    #success_url = reverse_lazy (request.GET['origin'])


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['endereco_form'] = EnderecoForm()
        return context
    

class DestinatarioUpdateView(UpdateView):
    model = Destinatario
    fields = '__all__'
    success_url = reverse_lazy('destinatarios-main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['endereco_form'] = EnderecoForm()
        return context

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
    model = Embalagem

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