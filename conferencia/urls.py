from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_xml, name='upload_xml'),
    path('salvar/', views.salvar_conferencia, name='salvar_conferencia'),
    # path('<str:nfe>deletar/', views.deletar_nfe, name='deletar'),
]
