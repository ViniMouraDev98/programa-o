from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_xml, name='upload_xml'),
    path('salvar/', views.salvar_conferencia, name='salvar_conferencia'),
    path('lista/', views.lista_conferencias, name='lista_conferencias'),
    path('deletar/<int:id>/', views.deletar_conferencia, name='deletar_conferencia'),
    path('gerar-pdf/<int:id>/', views.gerar_pdf_conferencia, name='gerar_pdf_conferencia'),
]
