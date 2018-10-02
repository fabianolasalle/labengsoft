from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import *
from django.core import serializers
from .models import *
import json

# Create your views here.

class EnderecoCreateView(CreateView):
    model = Endereco
    fields = '__all__'
    template_name = 'endereco_form.html'
    success_url = ''

class EnderecoDetailView(DetailView):
    model = Endereco
    template_name = 'endereco_detail.html'
    context_object_name = 'endereco'


class EnderecosView (ListView):
    model = Endereco
    template_name = 'endereco_list.html'

#def index(request):
#    return HttpResponse("Hello, world. Index!")
def enderecoByCepView (request, cep):
    try:
        endereco = serializers.serialize ('json', [ Endereco.getEnderecoByCep(str(cep)) ])
        return JsonResponse(endereco, safe=False)
    except Exception as ex:
        print (cep)
        raise

