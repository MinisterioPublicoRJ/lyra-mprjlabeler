import re

from django import forms
from .models import (
    Filtro,
    ClasseFiltro,
    ItemFiltro, Documento
)


# from filtro.task_utils.obter_num_processo import obter_list_cnpj_cpf


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            field = self.fields[key]
            if type(field.widget) == forms.TextInput:
                field.widget.attrs['class'] = 'form-control'
            elif (type(field.widget) == forms.SelectMultiple
                  or type(field.widget) == forms.Select):
                # selectpicker
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['data-style'] = 'form-control'
                field.widget.attrs['title'] = 'Selecione as Opções Desejadas'


class AdicionarFiltroForm(BaseModelForm):
    prefix = 'adicionar_filtro'

    class Meta:
        model = Filtro
        fields = ['nome', 'status', 'tipo_raspador', 'tipos_movimento', 'arquivo_tabulado', 'arquivo_documentos']
        widgets = {
            'status': forms.RadioSelect(attrs={'class': 'inline'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_raspador'].label = 'Tipo de Raspador'
        self.fields['tipos_movimento'].label = 'Tipo de Movimento'
        self.fields['arquivo_documentos'].label = 'Lista de Processos'


class AdicionarClasseForm(BaseModelForm):
    prefix = 'classe'
    idclasse = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )

    class Meta:
        model = ClasseFiltro
        fields = ['nome']


class ItemFiltroForm(BaseModelForm):
    prefix = 'itemfiltro'
    idclasse = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    idfiltro = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )
    iditemfiltro = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        regex = cleaned_data["regex"]
        termos = cleaned_data["termos"]
        if regex:
            try:
                re.compile(termos)
            except re.error:
                raise forms.ValidationError(
                    "A expressão regular contém um ou mais erros"
                )

        return cleaned_data

    class Meta:
        model = ItemFiltro
        fields = ['termos', 'tipo', 'regex']


# class FiltroNumProcessos(forms.Form):
#     """ """
#     cnpj = obter_list_cnpj_cpf()[:100]  # Limitando a 100 itens
#     numeros_processo = forms.ChoiceField(
#         label='N processos',
#         widget=forms.Select(
#             attrs={'class': 'fselectpicker form-control',
#                    'data-style': 'form-control',
#                    'title': 'Selecione as Opções Desejadas'}
#         ),
#         choices=cnpj,
#     )


# Filtro Form
class FiltroForm(forms.ModelForm):
    class Meta:
        model = Filtro
        fields = ['nome', 'situacao', 'status', 'tipo_raspador', 'tipos_movimento']


# ClasseFiltro Form
class ClasseFiltroForm(forms.ModelForm):
    class Meta:
        model = ClasseFiltro
        fields = '__all__'


# ItemFiltro Form
class ItemFiltroForm(forms.ModelForm):
    class Meta:
        model = ItemFiltro
        fields = '__all__'


# Documento Form
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'
