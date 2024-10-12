"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from petstore.views import CreateUsuarioView,GetUsuarioInfoView,UpdateUsuarioView,DeleteUsuarioView,CreatePetVIew,GetPetInfoView,DeletePetView,UpdatePetInfoView,CreateVetView,GetVetInfoView,UpdateVetInfoView,DeleteVetInfoView,UsuarioMarcaConsultaView,UsuarioVizualizaConsultaView,DefineDataConsultaView,DeleteConsultaView,DefineConsultaComoRealizadaView
from petstore.swagger import schema_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('novousuario',CreateUsuarioView.as_view(),name="criar_usuario"),
    path('info/<int:id_usuario>',GetUsuarioInfoView.as_view(),name="info_usuario"),
    path('atualizar/<int:id_usuario>',UpdateUsuarioView.as_view(),name="atualiza_usuario"),
    path('deletar/<int:id_usuario>',DeleteUsuarioView.as_view(),name="deleta_usuario"),
    path('criarconsulta/<int:id_usuario>',UsuarioMarcaConsultaView.as_view(),name="marca_consulta"),
    path('retornaconsulta/<int:id_consulta>',UsuarioVizualizaConsultaView.as_view(),name="retorna_consulta"),
    path('novopet',CreatePetVIew.as_view(),name="criar_pet"),
    path('infopet/<int:id_pet>',GetPetInfoView.as_view(),name="retorna_pet"),
    path('deletarpet/<int:id_pet>',DeletePetView.as_view(),name="deleta_pet"),
    path('atualizarpet/<int:id_pet>',UpdatePetInfoView.as_view(),name="atualiza_pet"),
    path('novovet',CreateVetView.as_view(),name="cadastra_veterinario"),
    path('buscarvet/<int:id_veterinario>',GetVetInfoView.as_view(),name="retorna_veterinario"),
    path('atualizarvet/<int:id_veterinario>',UpdateVetInfoView.as_view(),name="atualiza_vet"),
    path('deletarvet/<int:id_veterinario>',DeleteVetInfoView.as_view(),name="deleta_vet"),
    path('definirdataconsulta/<int:id_consulta>',DefineDataConsultaView.as_view(),name="define_data_consulta"),
    path('realizadaconsulta/<int:id_consulta>',DefineConsultaComoRealizadaView.as_view(),name="realiza_consulta"),
    path('deletarconsulta/<int:id_consulta>',DeleteConsultaView.as_view(),name="deletar_consulta"),
    path('swagger/',schema_view.with_ui('swagger',cache_timeout=0),name='schema-swagger-ui'),
]
