from django.urls import path

from . import views
from .views import *

urlpatterns = [
    #path('', views.index, name='index'),
    path('enderecos/', EnderecosView.as_view(), name='endereco-main'),
    path('enderecos/detail/<int:pk>', EnderecoDetailView.as_view(), name='endereco-detail'),
    path('enderecos/create/', EnderecoCreateView.as_view(), name='endereco-create'),
    path('enderecos/pesquisaCep/<cep>', views.enderecoByCepView, name='pesquisa-cep'),
]