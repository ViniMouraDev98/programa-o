from django.db import models
import json

class ConferenciaNFe(models.Model):
    # XML Data
    chave_acesso = models.CharField(max_length=50, unique=True, verbose_name="Chave de Acesso")
    numero_nota = models.CharField(max_length=20, verbose_name="Número da Nota")
    fornecedor = models.CharField(max_length=200, verbose_name="Fornecedor (Emitente)")
    cnpj_fornecedor = models.CharField(max_length=20, verbose_name="CNPJ do Fornecedor")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")
    data_emissao = models.DateField(verbose_name="Data de Emissão", null=True, blank=True)
    
    # Reviewer Data
    data_conferencia = models.DateTimeField(verbose_name="Data/Hora da Conferência")
    observacoes = models.TextField(verbose_name="Observações", blank=True, null=True)
    
    # JSON with full NFe extracted data
    dados_completos = models.JSONField(verbose_name="Dados Completos da NFe", null=True, blank=True)
    
    data_upload = (models.DateTimeField(auto_now_add=True, verbose_name="Data do Upload"))

    class Meta:
        verbose_name = "Conferência de NFe"
        verbose_name_plural = "Conferências de NFe"
        ordering = ['-data_conferencia']

    def __str__(self):
        return f"NFe {self.numero_nota} - {self.fornecedor}"