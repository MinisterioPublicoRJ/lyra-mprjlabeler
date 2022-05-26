"Web Views do módulo Labeler"
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.forms import AuthenticationForm
from .backends import Autenticador
from .models import Campanha
from .forms import RespostaForm


@login_required
def index(request):
    return render(request, 'labeler/index.html')


@login_required
def campanhas(request):
    "View para retornar lista de Campanhas"
    campanhas_ativas = Campanha.objects.filter(ativa=True)
    return render(
        request,
        'labeler/campanhas.html',
        {'campanhas': campanhas_ativas})


@login_required
def campanha(request, idcampanha, pedirnovo=False):
    "Tela para responder tarefas de campanha"
    campanha_ativa = get_object_or_404(Campanha, id=idcampanha)

    form = RespostaForm(campos=campanha_ativa.formulario.estrutura['campos'])

    tarefa = campanha_ativa.obter_tarefa(request.user.username, pedirnovo)

    if request.method == 'POST':
        form = RespostaForm(
            request.POST,
            campos=campanha_ativa.formulario.estrutura['campos'])
        form.is_valid()

        respostas = []

        for campo in form.fields:
            respostas += [{
                'nomecampo': campo,
                'resposta': str(form.cleaned_data[campo])
            }]

        tarefa.votar(request.user.username, respostas)

        tarefa = campanha_ativa.obter_tarefa(request.user.username)
        form = RespostaForm(
            campos=campanha_ativa.formulario.estrutura['campos'])

    if not tarefa:
        return render(
            request,
            'labeler/finalizado.html',
            {'campanha': campanha_ativa})

    return render(
        request,
        'labeler/pergunta.html', {
            'campanha': campanha_ativa,
            'tarefa': tarefa,
            'form': form
        })


def login(request):
    "Tela de login"
    status = 200

    if request.method == 'POST':
        # Autentica no SCA
        usuario = Autenticador().authenticate(request,
                                              request.POST.get('username', ''),
                                              request.POST.get('password', ''))
        if usuario:
            django_login(request, usuario)
            return redirect('campanhas')

        # Se não foi autenticado pelo SCA, tenta autenticar direto pelo Django.
        # O usuário deve ter sido cadastrado no Django pelo ADMIN ou qualquer outro modo.
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            django_login(request, form.get_user())
            return redirect('campanhas')
        else:
            messages.add_message(request, messages.ERROR, 'Usuário ou Senha inválidos')
            status = 403

    return render(request, 'labeler/login.html', status=status)


def logout(request):
    """Logout e Redirect para tela de login"""
    django_logout(request)
    return render(request, 'labeler/login.html')
