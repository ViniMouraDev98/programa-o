from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .utils import parse_nfe_xml
from .models import ConferenciaNFe
from datetime import datetime

def index(request):
    xmls = ConferenciaNFe.objects.all()
    return render(request, 'conferencia/index.html', {'xmls': xmls})

@require_POST
def upload_xml(request):
    """Receives the XML file, parses it, and returns the data as JSON."""
    if 'xml_file' not in request.FILES:
        return JsonResponse({'sucesso': False, 'erro': 'Nenhum arquivo enviado.'}, status=400)
    
    xml_file = request.FILES['xml_file']
    
    if not xml_file.name.endswith('.xml'):
        return JsonResponse({'sucesso': False, 'erro': 'Por favor, envie um arquivo .xml válido.'}, status=400)
    
    try:
        content = xml_file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            xml_file.seek(0)
            content = xml_file.read().decode('ISO-8859-1')
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': 'Erro ao decodificar o arquivo.'}, status=400)

    resultado = parse_nfe_xml(content)
    
    if resultado['sucesso']:
        return JsonResponse(resultado)
    else:
        return JsonResponse(resultado, status=400)

@require_POST
def salvar_conferencia(request):
    """Saves the reviewed data to the database."""
    try:
        chave_acesso = request.POST.get('chave_acesso')
        numero_nota = request.POST.get('numero_nota')
        fornecedor = request.POST.get('fornecedor')
        cnpj_fornecedor = request.POST.get('cnpj_fornecedor')
        valor_total = request.POST.get('valor_total')
        data_emissao_str = request.POST.get('data_emissao')
        
        data_conferencia_str = request.POST.get('data_conferencia')
        observacoes = request.POST.get('observacoes', '')
        
        import json
        dados_completos_str = request.POST.get('dados_completos')
        dados_completos = json.loads(dados_completos_str) if dados_completos_str else None

        if not all([chave_acesso, numero_nota, fornecedor, valor_total, data_conferencia_str]):
            return JsonResponse({'sucesso': False, 'erro': 'Dados obrigatórios faltando.'}, status=400)

        # Tratar datas
        data_emissao = None
        if data_emissao_str:
            data_emissao = datetime.strptime(data_emissao_str, '%Y-%m-%d').date()
            
        data_conferencia = datetime.strptime(data_conferencia_str, '%Y-%m-%dT%H:%M')

        # Check if already exists
        if ConferenciaNFe.objects.filter(chave_acesso=chave_acesso).exists():
            return JsonResponse({'sucesso': False, 'erro': 'Esta NFe já foi conferida e cadastrada.'}, status=400)

        ConferenciaNFe.objects.create(
            chave_acesso=chave_acesso,
            numero_nota=numero_nota,
            fornecedor=fornecedor,
            cnpj_fornecedor=cnpj_fornecedor,
            valor_total=valor_total,
            data_emissao=data_emissao,
            data_conferencia=data_conferencia,
            observacoes=observacoes,
            dados_completos=dados_completos
        )

        return JsonResponse({'sucesso': True, 'mensagem': 'Conferência salva com sucesso!'})

    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)
    
# def deletar_nfe(request, nfe):
