from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ConferenciaNFe
from datetime import datetime

# Sample dummy XML representing a minimal NFe
DUMMY_NFE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc versao="4.00" xmlns="http://www.portalfiscal.inf.br/nfe">
    <NFe>
        <infNFe Id="NFe12345678901234567890123456789012345678901234" versao="4.00">
            <ide>
                <nNF>12345</nNF>
                <serie>1</serie>
                <dhEmi>2023-10-01T10:00:00-03:00</dhEmi>
            </ide>
            <emit>
                <CNPJ>11222333000144</CNPJ>
                <xNome>Fornecedor Teste LTDA</xNome>
            </emit>
            <dest>
                <CNPJ>55666777000188</CNPJ>
                <xNome>Cliente Teste SA</xNome>
            </dest>
            <det nItem="1">
                <prod>
                    <cProd>PROD001</cProd>
                    <cEAN>7891011121314</cEAN>
                    <xProd>Produto de Teste 1</xProd>
                    <NCM>85171231</NCM>
                    <uCom>UN</uCom>
                    <qCom>10.00</qCom>
                    <vUnCom>100.00</vUnCom>
                    <vProd>1000.00</vProd>
                    <xPed>PED-999</xPed>
                </prod>
            </det>
            <total>
                <ICMSTot>
                    <vNF>1000.00</vNF>
                </ICMSTot>
            </total>
            <transp>
                <vol>
                    <qVol>2</qVol>
                    <esp>CAIXA</esp>
                    <pesoL>15.500</pesoL>
                    <pesoB>16.000</pesoB>
                </vol>
            </transp>
            <infAdic>
                <infCpl>Entregar em horario comercial.</infCpl>
            </infAdic>
        </infNFe>
    </NFe>
</nfeProc>
"""

class ConferenciaNFeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('upload_xml')
        self.salvar_url = reverse('salvar_conferencia')

    def test_homepage_loads(self):
        """Verify the homepage renders correctly."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conferência de NFe")

    def test_xml_upload_and_parse(self):
        """Test uploading an XML file returns the parsed data in JSON."""
        xml_file = SimpleUploadedFile(
            "nota_teste.xml",
            DUMMY_NFE_XML.encode('utf-8'),
            content_type="application/xml"
        )
        response = self.client.post(self.upload_url, {'xml_file': xml_file})
        self.assertEqual(response.status_code, 200)
        
        json_data = response.json()
        self.assertTrue(json_data['sucesso'])
        
        dados = json_data['dados']
        self.assertEqual(dados['chave_acesso'], "12345678901234567890123456789012345678901234")
        self.assertEqual(dados['numero_nota'], "12345")
        self.assertEqual(dados['fornecedor'], "Fornecedor Teste LTDA")
        self.assertEqual(dados['valor_total'], 1000.0)
        self.assertEqual(dados['quantidade_volumes'], "2")
        self.assertEqual(dados['produtos'][0]['descricao'], "Produto de Teste 1")

    def test_salvar_conferencia(self):
        """Test saving the review data."""
        payload = {
            'chave_acesso': '12345678901234567890123456789012345678901234',
            'numero_nota': '12345',
            'fornecedor': 'Fornecedor Teste LTDA',
            'cnpj_fornecedor': '11222333000144',
            'valor_total': '1000.00',
            'data_emissao': '2023-10-01',
            'data_conferencia': '2026-05-13T10:00',
            'observacoes': 'Tudo certo',
            'dados_completos': '{"produtos": []}'
        }
        
        response = self.client.post(self.salvar_url, payload)
        self.assertEqual(response.status_code, 200)
        
        json_data = response.json()
        self.assertTrue(json_data['sucesso'])
        
        # Verify it was saved in DB
        self.assertEqual(ConferenciaNFe.objects.count(), 1)
        conf = ConferenciaNFe.objects.first()
        self.assertEqual(conf.chave_acesso, '12345678901234567890123456789012345678901234')
        self.assertEqual(conf.observacoes, 'Tudo certo')

    def test_duplicate_conferencia(self):
        """Test preventing duplicate saving of the same NFe."""
        payload = {
            'chave_acesso': 'DUPLICATE123',
            'numero_nota': '123',
            'fornecedor': 'Teste',
            'cnpj_fornecedor': '111',
            'valor_total': '100.00',
            'data_conferencia': '2026-05-13T10:00'
        }
        
        # Save first time
        resp1 = self.client.post(self.salvar_url, payload)
        self.assertEqual(resp1.status_code, 200)
        
        # Try to save again
        resp2 = self.client.post(self.salvar_url, payload)
        self.assertEqual(resp2.status_code, 400) # Should fail
        self.assertFalse(resp2.json()['sucesso'])
        self.assertIn('já foi conferida', resp2.json()['erro'])
