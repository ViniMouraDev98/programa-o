from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from .utils import parse_nfe_xml
from .models import ConferenciaNFe
from datetime import datetime
from xhtml2pdf import pisa
def index(request):
    """Renders the main page with upload form and modal."""
    return render(request, 'conferencia/index.html')

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

def lista_conferencias(request):
    conferencias = ConferenciaNFe.objects.all()
    return render(request, 'conferencia/lista.html', {'conferencias': conferencias})

def deletar_conferencia(request, id):
    conferencia = get_object_or_404(ConferenciaNFe, id=id)
    if request.method == 'POST':
        conferencia.delete()
        messages.success(request, 'Conferência deletada com sucesso.')
        return redirect('lista_conferencias')
    return redirect('lista_conferencias')

def gerar_pdf_conferencia(request, id):
    conferencia = get_object_or_404(ConferenciaNFe, id=id)
    template_path = 'conferencia/pdf_report.html'
    context = {'conferencia': conferencia, 'produtos': conferencia.dados_completos.get('produtos', []) if conferencia.dados_completos else []}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="conferencia_{conferencia.numero_nota}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Tivemos erros ao gerar o PDF', status=500)
    return response
