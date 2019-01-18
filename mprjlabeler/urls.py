"""mprjlabeler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.views.generic.base import RedirectView
from django.contrib.auth.views import logout
from django.conf.urls.static import static
from django.conf import settings
from labeler.views import campanhas, campanha, login, index
from labeler.api import tarefa
from filtro.views import (
    filtros,
    adicionar_filtro,
    filtro,
    excuir_filtro,
    adicionar_classe
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('campanhas/', campanhas, name='campanhas'),
    path('campanhas/<int:idcampanha>/',
         campanha,
         name='campanha'),
    path('campanhas/<int:idcampanha>/pedirnovo/',
         campanha,
         {'pedirnovo': True},
         name='nova_campanha'),
    path('login/', login, name='login'),
    path('', index, name='index'),
    path('logout/',
         logout,
         {'next_page': '/'},
         name='logout'),
    path('api/tarefa/<int:idcampanha>/',
         tarefa,
         name='api_tarefa'),
    path(
        'filtros/',
        filtros,
        name='filtros'
    ),
    path(
        'filtros/adicionar',
        adicionar_filtro,
        name='filtros-adicionar'
    ),
    path(
        'filtros/<int:idfiltro>',
        filtro,
        name='filtros-filtro'
    ),
    path('filtros/excluir', excuir_filtro, name='filtros-excluir'),
    path('filtros/adicionar-classe/<int:idfiltro>', adicionar_classe, name='filtros-adicionar-classe'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
