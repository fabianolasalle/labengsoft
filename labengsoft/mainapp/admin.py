from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(SigepEnvironment)
admin.site.register(Servico)
admin.site.register(CartaoPostagem)
admin.site.register(Endereco)
admin.site.register(GrupoDestinatario)
admin.site.register(Telefone)
admin.site.register(Destinatario)
admin.site.register(Remetente)
admin.site.register(Embalagem)
admin.site.register(ObjetoPostal)
admin.site.register(PreListaPostagem)