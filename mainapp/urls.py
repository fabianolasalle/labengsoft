from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    #path('enderecos/', EnderecosView.as_view(), name='enderecos-main'),
    path('enderecos/update/<int:pk>', EnderecoUpdateView.as_view(), name='enderecos-update'),
    path('enderecos/delete/<int:pk>', EnderecoDeleteView.as_view(), name='enderecos-delete'),
    #path('enderecos/detail/<int:pk>', EnderecoDetailView.as_view(), name='enderecos-detail'),
    path('enderecos/create/', EnderecoCreateView.as_view(), name='enderecos-create'),
    path('enderecos/pesquisaCep/<cep>', views.enderecoByCepView, name='pesquisa-cep'),


    path('destinatarios/', DestinatariosView.as_view(), name='destinatarios-main'),
    path('destinatarios/update/<int:pk>', DestinatarioUpdateView.as_view(), name='destinatarios-update'),
    path('destinatarios/delete/<int:pk>', DestinatarioDeleteView.as_view(), name='destinatarios-delete'),
    path('destinatarios/detail/<int:pk>', DestinatarioDetailView.as_view(), name='destinatarios-detail'),
    path('destinatarios/create/', DestinatarioCreateView.as_view(), name='destinatarios-create'),

    path('grupodest/', GruposDestView.as_view(), name='grupodest-main'),
    path('grupodest/update/<int:pk>', GrupoDestUpdateView.as_view(), name='grupodest-update'),
    path('grupodest/delete/<int:pk>', GrupoDestDeleteView.as_view(), name='grupodest-delete'),
    path('grupodest/detail/<int:pk>', GrupoDestDetailView.as_view(), name='grupodest-detail'),
    path('grupodest/create/', GrupoDestCreateView.as_view(), name='destinatarios-create'),

    #path('grupodest/', TelefonesView.as_view(), name='destinatarios-main'),
    #path('grupodest/update/<int:pk>', DestinatarioUpdateView.as_view(), name='destinatarios-update'),
    #path('grupodest/delete/<int:pk>', DestinatarioDeleteView.as_view(), name='destinatarios-delete'),
    #path('grupodest/detail/<int:pk>', DestinatarioDetailView.as_view(), name='destinatarios-detail'),
    #path('grupodest/create/', DestinatarioCreateView.as_view(), name='destinatarios-create'),
]