from django.urls import path
from . import views

app_name = 'filtro'

urlpatterns = [
    path('', views.FiltroListView.as_view(), name='list'),
    path('adicionar', views.CadastrarFiltro.as_view(), name='adicionar'),
    path('filtros/<int:pk>', views.AlterarFiltro.as_view(), name='alterar'),
    path('excluir/<int:pk>', views.ExcluirFiltro.as_view(), name='excluir'),

    path('classe/novo/', views.ClasseCreateView.as_view(), name='classe_create'),
    path('classe/<int:pk>/editar/', views.ClasseUpdateView.as_view(), name='classe_update'),
    path('classe/<int:pk>/excluir/', views.ClasseDeleteView.as_view(), name='classe_delete'),
    path('get_classe_data/', views.GetClasseDataView.as_view(), name='get_classe_data'),
]
