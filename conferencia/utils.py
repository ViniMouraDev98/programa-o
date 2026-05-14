import xmltodict
from datetime import datetime

def parse_nfe_xml(xml_content):
    """
    Parses NFe XML content and extracts key data.
    Assumes standard NFe layout (nfeProc -> NFe -> infNFe).
    """
    try:
        # Parse XML to dictionary
        doc = xmltodict.parse(xml_content)
        
        # Determine root (sometimes it's directly NFe, sometimes wrapped in nfeProc)
        if 'nfeProc' in doc:
            nfe = doc['nfeProc']['NFe']['infNFe']
        elif 'NFe' in doc:
            nfe = doc['NFe']['infNFe']
        else:
            raise ValueError("O arquivo não possui o formato padrão de NFe.")

        # Extract basic sections
        chave = nfe['@Id'].replace('NFe', '')
        ide = nfe.get('ide', {})
        emit = nfe.get('emit', {})
        dest = nfe.get('dest', {})
        total = nfe.get('total', {}).get('ICMSTot', {})
        transp = nfe.get('transp', {})
        infAdic = nfe.get('infAdic', {})

        numero_nota = ide.get('nNF', '')
        serie = ide.get('serie', '')
        data_emissao_str = ide.get('dhEmi', '')[:10] if ide.get('dhEmi') else None
        
        fornecedor = emit.get('xNome', '')
        cnpj_fornecedor = emit.get('CNPJ', '')
        
        destinatario = dest.get('xNome', '')

        valor_total = float(total.get('vNF', '0.00'))

        # Volume Data
        vol = transp.get('vol', {})
        if isinstance(vol, list) and len(vol) > 0:
            vol = vol[0] # Pegar o primeiro volume para simplificar, ou somar se necessário

        qVol = vol.get('qVol', '')
        esp = vol.get('esp', '')
        pesoB = vol.get('pesoB', '')
        pesoL = vol.get('pesoL', '')

        # Complementary Info
        infCpl = infAdic.get('infCpl', '')

        # Products Data
        det = nfe.get('det', [])
        if not isinstance(det, list):
            det = [det]
            
        produtos = []
        for item in det:
            prod = item.get('prod', {})
            produtos.append({
                'descricao': prod.get('xProd', ''),
                'codigo': prod.get('cProd', ''),
                'ean': prod.get('cEAN', ''),
                'ncm': prod.get('NCM', ''),
                'unidade': prod.get('uCom', ''),
                'pedido': prod.get('xPed', '')
            })

        return {
            'sucesso': True,
            'dados': {
                'chave_acesso': chave,
                'numero_nota': numero_nota,
                'serie': serie,
                'fornecedor': fornecedor,
                'cnpj_fornecedor': cnpj_fornecedor,
                'destinatario': destinatario,
                'valor_total': valor_total,
                'data_emissao': data_emissao_str,
                'quantidade_volumes': qVol,
                'especie_volumes': esp,
                'peso_bruto': pesoB,
                'peso_liquido': pesoL,
                'info_complementar': infCpl,
                'produtos': produtos
            }
        }

    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao processar XML: {str(e)}'
        }
