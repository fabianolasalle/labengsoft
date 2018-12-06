from django import forms
from .models import *
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin

class EnderecoForm (PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf']
        