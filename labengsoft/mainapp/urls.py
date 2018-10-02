from django.urls import path

from . import views
from .views import *

urlpatterns = [
    #path('', views.index, name='index'),
    path('enderecos/', EnderecosView.as_view(), name='enderecos-main'),
    path('enderecos/update/<int:pk>', EnderecoUpdateView.as_view(), name='enderecos-update'),
    path('enderecos/delete/<int:pk>', EnderecoDeleteView.as_view(), name='enderecos-delete'),
    path('enderecos/detail/<int:pk>', EnderecoDetailView.as_view(), name='enderecos-detail'),
    path('enderecos/create/', EnderecoCreateView.as_view(), name='enderecos-create'),
    path('enderecos/pesquisaCep/<cep>', views.enderecoByCepView, name='pesquisa-cep'),


    path('destinatarios/', DestinatariosView.as_view(), name='destinatarios-main'),
    path('destinatarios/update/<int:pk>', DestinatarioUpdateView.as_view(), name='destinatarios-update'),
    path('destinatarios/delete/<int:pk>', DestinatarioDeleteView.as_view(), name='destinatarios-delete'),
    path('destinatarios/detail/<int:pk>', DestinatarioDetailView.as_view(), name='destinatarios-detail'),
    path('destinatarios/create/', DestinatarioCreateView.as_view(), name='destinatarios-create'),

    path('telefones/', TelefonesView.as_view(), name='destinatarios-main'),
    path('telefones/update/<int:pk>', DestinatarioUpdateView.as_view(), name='destinatarios-update'),
    path('telefones/delete/<int:pk>', DestinatarioDeleteView.as_view(), name='destinatarios-delete'),
    path('telefones/detail/<int:pk>', DestinatarioDetailView.as_view(), name='destinatarios-detail'),
    path('telefones/create/', DestinatarioCreateView.as_view(), name='destinatarios-create'),
]