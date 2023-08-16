"""Modulo responsável por processar arquivo csv contendo extração TJ, feita pelo Anderson.
   O modulo deve receber cnpj ou cpf validos e retornar lista com todos os números de processos referente
   ao dado fornecido.

   Provavelmente essas informações serão disponibilizadas no banco de dados, nesse momento,17/03/2022,
   estou utilizando o arquivo csv somente para testes.
 """
import csv
import re
from pathlib import Path
from collections import namedtuple

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'mprjlabeler.settings'

import django

django.setup()

from processos.models import ReusProcessosColetados


# def processa_arquivo():
#     root_path = Path(__file__).parent.absolute()
#     file = Path(root_path, 'novas_acoes_individuais_consumeristas_2_parcial_4.csv')
#     list_data_full = []
#     with open(file, 'r', encoding='ISO-8859-1') as f:
#         data_full = csv.reader(f, delimiter=';')
#
#         # Processando arquivo
#         for row in data_full:
#             list_data_full.append(tuple(row))
#
#     list_data_full = list_data_full[1:]
#
#     # Mapeando valores e campos com namedtuple. Objetivo principal, legibilidade
#     fields = ('numero_processo', 'réu', 'cnpj_cpf')
#     data = namedtuple('Data', fields)
#     list_data = []
#     for data in map(data._make, list_data_full):
#         list_data.append(data)
#
#     return list_data


# def obter_list_cnpj_cpf():
#     # Retorna lista de cnpj/cpf válidos e unicos
#     # Criando e tratando listagem cnpj/cpf
#     list_data_full = processa_arquivo()
#     list_cnpj = []
#     cnpj_cpf = None
#     for row in list_data_full:
#         # pegar todos que não contem somente zeros
#         if not re.match('^0*$', row.cnpj_cpf):
#             cnpj_cpf = row.cnpj_cpf
#
#             # Completando com zeros a esquerda cnpjs que sejam menor que 14 dígitos
#             if len(row.cnpj_cpf) < 14 and len(row.cnpj_cpf) != 11:
#                 cnpj_cpf = row.cnpj_cpf.zfill(14)
#
#             list_cnpj.append((cnpj_cpf, cnpj_cpf))
#
#     cnpj = sorted(set(list_cnpj))
#     return cnpj


# def obter_numeros_processos(cnpj_cpf):
#     list_data_full = processa_arquivo()
#     cnpj_cpf = cnpj_cpf
#     list_processos = []
#     for row in list_data_full:
#         if row.cnpj_cpf == cnpj_cpf:
#             # + '\n'
#             list_processos.append(row.numero_processo.replace('.', '').replace('-', ''))
#     return list_processos

def obter_numeros_processos(alvo):
    n_processos = ReusProcessosColetados.objects.using('proc_base').filter(pessoa_reu__unaccent__trigram_similar=alvo)
    n_processos = n_processos.values_list('processo_numero', flat=True)

    return n_processos


if __name__ == '__main__':
    procs = obter_numeros_processos('MINISTERIO PUBLICO')

    print(procs)
    # for i in procs:
    #     print(i[0])
