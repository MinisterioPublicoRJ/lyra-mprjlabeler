import json
import os
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.db import connection
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.http import (
    JsonResponse,
    StreamingHttpResponse,
    HttpResponse,
    Http404, HttpResponseRedirect
)
from wsgiref.util import FileWrapper
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from .forms import (
    AdicionarFiltroForm,
    FiltroForm,
    AdicionarClasseForm,
    ItemFiltroForm,
    # FiltroNumProcessos,
)
from filtro.models import (
    Filtro,
    ClasseFiltro,
    ItemFiltro,
    UsuarioAcessoFiltro
)
from .tasks import (
    submeter_classificacao,
    classificar_baixados,
    compactar,
)
from .task_utils.functions import montar_estrutura_filtro


def obter_filtro(idfiltro, username, responsavel=True):
    base = obter_filtros(username, responsavel)

    return get_object_or_404(
        base,
        pk=idfiltro
    )


def obter_filtros(username, responsavel=True):
    if responsavel:
        return Filtro.objects.filter(responsavel=username)

    return Filtro.objects.filter(
        (Q(responsavel=username) | Q(usuarioacessofiltro__usuario=username))
    ).distinct()


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


@login_required
def filtros(request):
    novo_filtro_form = AdicionarFiltroForm

    return render(
        request,
        'filtro/filtros.html',
        {
            'filtros': obter_filtros(request.user.username),
            'novofiltroform': novo_filtro_form
        }
    )


@login_required
def lista_usuarios(request):
    term = request.GET.get("term")
    usuarios_regulares = get_user_model().objects.filter(
        ~Q(username=request.user.username),
        username__icontains=term,
        is_staff=False,
        is_superuser=False,
    )
    return JsonResponse(
        [str(u.username) for u in usuarios_regulares],
        safe=False
    )


def obter_contadores_filtro(filtro):
    query = """select
        case when filtro_classefiltro.nome is null then 'Sem Classificação'
        else filtro_classefiltro.nome end nomeclasse,
        classe,
        count(classe) total
        from (
        SELECT distinct
        case when classe_filtro_id is null then 0
        else classe_filtro_id end classe,
        numero
        FROM filtro_documento
        WHERE "filtro_documento"."filtro_id" = %s) tabela
        left join filtro_classefiltro on
        tabela.classe = filtro_classefiltro.id
        GROUP BY nomeclasse, classe
        ORDER BY "total" desc"""

    with connection.cursor() as cursor:
        cursor.execute(query, [filtro.id])
        return dictfetchall(cursor)


def preencher_estrutura_inicial(m_filtro, estrutura):
    mapper = [
        ("regex", '1'),
        ("regex_reforco", '2'),
        ("regex_exclusao", '3'),
        ("regex_invalidacao", '4'),
        ("coadunadas", '5')
    ]
    for classe in estrutura:
        m_classe = ClasseFiltro()
        m_classe.filtro = m_filtro
        m_classe.nome = classe['nome']
        m_classe.save()
        for parametro, tipo in mapper:
            [
                ItemFiltro(
                    classe_filtro=m_classe,
                    termos=regex,
                    tipo=tipo,
                    regex=True
                ).save()
                for regex in classe['parametros'][parametro]
            ]


@login_required
@require_http_methods(['POST'])
def adicionar_filtro(request):
    form = AdicionarFiltroForm(request.POST, request.FILES)
    form.instance.responsavel = request.user.username

    form.save()

    if form.files:
        preencher_estrutura_inicial(
            form.instance,
            json.loads(form.files['adicionar_filtro-estrutura'].read())
        )

    messages.success(
        request,
        "Filtro %s adicionado e salvo" % form.instance.nome)

    return redirect(
        reverse(
            'filtros-filtro',
            args=[form.instance.id]
        )
    )


@login_required
def filtro(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username)
    form = FiltroForm(instance=m_filtro)
    # form_proc = FiltroNumProcessos()

    if request.method == 'POST':
        form = FiltroForm(
            request.POST,
            request.FILES,
            instance=m_filtro
        )
        form.is_valid()
        form.save()

        messages.success(request, "Filtro salvo!")

    return render(
        request,
        'filtro/filtro.html',
        {
            'form': form,
            # 'form_proc': form_proc,
            'model': m_filtro,
            'idfiltro': idfiltro,
            'adicionarclasseform': AdicionarClasseForm(),
            'itemfiltroform': ItemFiltroForm(),
            'is_filtro_owner': m_filtro.responsavel == request.user.username
        }
    )


@login_required
@require_http_methods(['POST'])
def excuir_filtro(request):
    idfiltro = request.POST.get('idfiltroexcluir')

    m_filtro = obter_filtro(idfiltro, request.user.username)
    m_filtro.delete()

    messages.success(request, 'Filtro removido com Sucesso!')
    return redirect(
        reverse(
            'filtros',
        )
    )


@login_required
@require_http_methods(['POST'])
def adicionar_classe(request, idfiltro):
    f_adicionar = AdicionarClasseForm(request.POST)

    if not f_adicionar.is_valid():
        return None

    if f_adicionar.cleaned_data['idclasse']:
        f_adicionar = AdicionarClasseForm(
            request.POST,
            instance=get_object_or_404(
                ClasseFiltro,
                pk=f_adicionar.cleaned_data['idclasse'])
        )

        f_adicionar.save()
        messages.success(request, 'Classe de Filtro alterada com sucesso!')
    else:
        m_filtro = obter_filtro(idfiltro, request.user.username)

        f_adicionar.instance.filtro = m_filtro
        f_adicionar.instance.ordem = len(m_filtro.classefiltro_set.all())
        f_adicionar.save()

        messages.success(request, 'Classe de Filtro adicionada!')

    return redirect(
        reverse(
            'filtros-filtro',
            args=[idfiltro]
        )
    )


@login_required
@require_http_methods(['POST'])
def excluir_classe(request, idfiltro, idclasse):
    m_classe = get_object_or_404(
        ClasseFiltro,
        pk=idclasse,
        filtro__id=idfiltro
    )

    m_classe.delete()

    messages.warning(request, 'Classe de filtro removida')

    return redirect(
        reverse(
            'filtros-filtro',
            args=[idfiltro]
        )
    )


@login_required
@require_http_methods(['GET'])
def mover_classe(request, idfiltro, idclasse, direcao):
    m_classe = get_object_or_404(
        ClasseFiltro,
        pk=idclasse,
        filtro__id=idfiltro)

    if direcao == 'acima':
        m_classe.up()

    else:
        m_classe.down()

    messages.success(request, 'Classe movida %s!' % direcao)

    return redirect(
        reverse(
            'filtros-filtro',
            args=[idfiltro]
        )
    )


@login_required
@require_http_methods(['POST'])
def adicionar_itemfiltro(request):
    f_itemfiltro = ItemFiltroForm(request.POST)

    if f_itemfiltro.is_valid():
        if f_itemfiltro.cleaned_data['iditemfiltro']:
            m_itemfiltro = get_object_or_404(
                ItemFiltro,
                pk=f_itemfiltro.cleaned_data['iditemfiltro']
            )

            f_itemfiltro = ItemFiltroForm(
                request.POST,
                instance=m_itemfiltro)

            f_itemfiltro.save()

            messages.success(request, 'Item de Filtro alterado!')
        else:
            f_itemfiltro.instance.classe_filtro = get_object_or_404(
                ClasseFiltro,
                pk=f_itemfiltro.cleaned_data['idclasse'])

            f_itemfiltro.save()

            messages.success(request, 'Item de Filtro adicionado!')

    else:
        messages.error(request, f_itemfiltro.errors["__all__"])

    return redirect(
        reverse(
            'filtros-filtro',
            args=[f_itemfiltro.cleaned_data['idfiltro']]
        )
    )


@login_required
@require_http_methods(['GET'])
def excluir_item_filtro(request, idfiltro, iditemfiltro):
    m_itemfiltro = get_object_or_404(ItemFiltro, pk=iditemfiltro)

    m_itemfiltro.delete()

    messages.warning(request, 'Item de Filtro removido com sucesso!')

    return redirect(
        reverse(
            'filtros-filtro',
            args=[idfiltro]
        )
    )


@login_required
@require_http_methods(['GET'])
def classificar(request, idfiltro):
    submeter_classificacao.delay(idfiltro)

    messages.info(
        request,
        ('Filtro submetido para classificação! Acompanhe o '
         'andamento pela tela de gestão dos filtros.')
    )

    return redirect(
        reverse(
            'filtros'
        )
    )


@login_required
@require_http_methods(['GET'])
def reaplicar_filtro(request, idfiltro):
    classificar_baixados.delay(idfiltro)

    messages.info(
        request,
        ('Filtro submetido para reclassificação! Acompanhe o '
         'andamento pela tela de gestão dos filtros.')
    )

    return redirect(
        reverse(
            'filtros'
        )
    )


@login_required
@require_http_methods(['GET'])
def obter_situacao(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username)

    return JsonResponse(
        {
            'situacao': m_filtro.situacao,
            'percentual': m_filtro.percentual_atual,
            'descricao': m_filtro.get_situacao_display(),
            'disponivel': m_filtro.saida.url if m_filtro.saida.name else None
        }
    )


@login_required
@require_http_methods(['GET'])
def listar_resultados(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username)

    classe = request.GET.get('classe', 'T')

    sumario = m_filtro.documento_set.all().values(
        'classe_filtro__nome').annotate(
        total=Count('classe_filtro__nome')).order_by(
        '-total')

    documentos = m_filtro.documento_set

    sumario = obter_contadores_filtro(m_filtro)

    total_classificados = sum(
        item['total']
        for item in sumario
        if item['classe'] != 0
    )
    total_documentos = documentos.distinct('numero').count()

    for item in sumario:
        item['percentual_classe'] = 0 if not total_classificados \
            else (item['total'] * 100.0) / total_classificados
        item['percentual_total'] = 0 if not total_documentos \
            else (item['total'] * 100.0) / total_documentos

    if classe == 'T':
        documentos = documentos.all()
    elif classe == '0':
        documentos = documentos.filter(classe_filtro__isnull=True)
    else:
        documentos = documentos.filter(classe_filtro=classe).all()

    total = documentos.distinct('numero').count()
    paginator = Paginator(documentos, 25)

    page = request.GET.get('page', 1)
    documentos = paginator.get_page(page)

    return render(
        request,
        'filtro/resultados.html',
        {
            'documentos': documentos,
            'filtro': m_filtro,
            'sumario': sumario,
            'total_classificados': total_classificados,
            'total_documentos': total_documentos,
            'total': total,
            'classe': classe,
            'mostra_lda': m_filtro.saida_lda is not None
        }
    )


@login_required
@require_http_methods(['GET'])
def executar_compactacao(request, idfiltro):
    compactar.delay(idfiltro)

    messages.info(
        request,
        ('Filtro submetido para compactação! Acompanhe o '
         'andamento pela tela de gestão dos filtros.')
    )

    return redirect(
        reverse(
            'filtros'
        )
    )


@login_required
@require_http_methods(['GET'])
def baixar_estrutura(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username)

    estrutura = json.dumps(montar_estrutura_filtro(m_filtro, True))
    response = HttpResponse(estrutura, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=estrutura.json'

    return response


@login_required
@require_http_methods(['GET'])
def mediaview(request, mediafile):
    del request
    fullfile = os.path.join(settings.MEDIA_ROOT, mediafile)
    response = StreamingHttpResponse(
        FileWrapper(open(fullfile, 'rb'), 8192)
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % mediafile
    response['X-Sendfile'] = smart_str(fullfile)
    return response


@login_required
@require_http_methods(['GET'])
def explorar_lda(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username)
    return HttpResponse(m_filtro.saida_lda)


@login_required
@require_http_methods(['GET'])
def get_usuarios_acessos(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username, True)

    return JsonResponse(
        [
            str(usuario.usuario)
            for usuario in m_filtro.usuarioacessofiltro_set.all()
        ],
        safe=False
    )


@login_required
@require_http_methods(['POST'])
def adicionar_usuario_filtro(request, idfiltro):
    m_filtro = obter_filtro(idfiltro, request.user.username, True)
    username = request.POST.get('compartilhar_username')

    if m_filtro.responsavel == request.user.username:
        obj, created = UsuarioAcessoFiltro.objects.get_or_create(
            filtro=m_filtro,
            usuario=username
        )

        status = 200 if created else 400
    else:
        raise Http404

    return JsonResponse({'created': created}, status=status)


class FiltroListView(LoginRequiredMixin, ListView):
    model = Filtro
    template_name = 'filtro/filtros.html'


class CadastrarFiltro(LoginRequiredMixin, CreateView):
    model = Filtro
    form_class = AdicionarFiltroForm
    success_url = reverse_lazy('filtro:list')

    def get_success_url(self):
        return reverse('filtros:alterar', args=[self.object.id])

    def form_valid(self, form):
        form = AdicionarFiltroForm(self.request.POST, self.request.FILES)
        form.instance.responsavel = self.request.user.username

        form.save()

        messages.success(
            self.request,
            "Filtro %s adicionado e salvo" % form.instance.nome)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Erro ao adicionar filtro: %s" % form.errors
        )

        return super().form_invalid(form)


class AlterarFiltro(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Filtro
    form_class = AdicionarFiltroForm
    success_url = reverse_lazy('filtro:list')
    success_message = 'Filtro alterado com sucesso!'

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Erro ao adicionar filtro: %s" % form.errors
        )

        return super().form_invalid(form)


class ExcluirFiltro(LoginRequiredMixin, DeleteView):
    model = Filtro
    success_url = reverse_lazy('filtros')

    def get(self, request, *args, **kwargs):
        object = self.get_object()

        for classe in object.classefiltro_set.all():
            classe.itemfiltro_set.all().delete()
            classe.delete()

        object.delete()

        messages.success(
            request, 'Filtro removido com sucesso!'
        )

        return HttpResponseRedirect(reverse('filtro:list'))


@method_decorator(csrf_exempt, name='dispatch')
class ClasseCreateView(View):
    def post(self, request):
        nome = request.POST.get('nome')
        filtro = request.POST.get('filtroId')
        ClasseFiltro.objects.create(
            nome=nome,
            filtro_id=filtro
        )
        return JsonResponse({}, status=200)


class ClasseUpdateView(View):
    def post(self, request, pk):
        classe = get_object_or_404(ClasseFiltro, pk=pk)
        if request.is_ajax():
            form = UpdateClasseForm(request.POST, instance=classe)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)


class ClasseDeleteView(View):
    def post(self, request, pk):
        classe = get_object_or_404(ClasseFiltro, pk=pk)
        if request.is_ajax():
            classe.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class GetClasseDataView(View):
    def get(self, request):
        classes = ClasseFiltro.objects.filter(filtro_id=request.GET.get('filtroId'))
        data = [{'id': classe.pk, 'nome': classe.nome, 'termos': [{'id': termo.pk for termo in classe.itemfiltro_set.all()}]} for classe in classes]
        return JsonResponse(data, safe=False)
