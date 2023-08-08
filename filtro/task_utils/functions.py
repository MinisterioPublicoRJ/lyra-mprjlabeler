import logging
import re
from classificador_lyra.regex import constroi_classificador_dinamica
# from processostjrj.mni import consulta_processo, cria_cliente
from slugify import slugify
from filtro.models import Documento
# from filtro.task_utils.iniciais import processar as processar_iniciais

logger = logging.getLogger(__name__)


def limpar_documentos(m_filtro):
    m_filtro.documento_set.all().delete()


def parse_documentos(m_filtro):
    m_filtro.arquivo_documentos.open(mode='r')
    retorno = m_filtro.arquivo_documentos.readlines()
    m_filtro.arquivo_documentos.close()
    return retorno


# def download_processos(documentos, trazer_iniciais=False):
#     from processostjrj.mni import consulta_processo, cria_cliente
#     cliente = cria_cliente()
#     for numero in documentos:
#         iniciais = []
#         f_numero = numero.strip().zfill(20)
#         if not numero:
#             continue
#         try:
#             processo = consulta_processo(
#                 cliente,
#                 f_numero,
#                 movimentos=True,
#                 _value_1=[{"incluirCabecalho": True}]
#             )
#             if trazer_iniciais:
#                 iniciais = processar_iniciais(f_numero)
#
#         except Exception as error:
#             logger.error('Erro no download do processo %s' % numero, error)
#             continue
#         yield (numero, processo, iniciais)


def parse_documento(tipos_movimento, processo):
    retorno = []
    if (not processo.sucesso or
            not processo.processo or
            'movimento' not in processo.processo):
        return retorno

    for tipo in tipos_movimento:
        documentos = filter(
            lambda x: re.findall(
                tipo.nome_tj,
                x.movimentoLocal.descricao,
                re.IGNORECASE),
            [mv for mv in processo.processo.movimento if mv.movimentoLocal]
        )

        for documento in documentos:
            inteiro_teores = filter(
                lambda x: re.findall(r'^Descrição: ', x, re.IGNORECASE),
                documento.complemento
            )
            for inteiro_teor in inteiro_teores:
                retorno.append(
                    (processo.processo.dadosBasicos.numero, tipo, inteiro_teor)
                )
    return retorno


def obtem_documento_final(pre_documentos, m_filtro):
    for pre_documento in pre_documentos:
        m_documento = Documento()
        m_documento.filtro = m_filtro
        m_documento.numero = pre_documento[0]
        m_documento.tipo_movimento = pre_documento[1]
        m_documento.conteudo = pre_documento[2]
        m_documento.save()


def converte_and_regex(termos):
    """
    Converte o conectivo "e" em "&" e aplica expressões regulares a uma string de termos.

    Args:
        termos (str): Uma string contendo os termos a serem processados.

    Returns:
        str: A string modificada após a aplicação das substituições e expressões regulares.

    Example:
        >>> converte_and_regex("termo1 e termo2")
        '((?i)termo1) & ((?i)termo2)'

    OBS:
        Eu imagino que de para fazer uma função menor, porém preferir deixar dessa maneira
        pelo meu conhecimento limitado, nesse momento, e que assim eu achei que ficaria
        um codigo mais inclusivo.
    """

    # Substituir o conectivo " e " por "&"
    string_modificado = re.sub(r'(\s*E\s* | \s*e\s*)', '&', termos)

    # Encontrar todas as ocorrências de termos com "&"
    pattern_and = r"\S*\&\S*"
    list_termos = tuple(re.findall(pattern_and, string_modificado))

    # Modificar a string substituindo os termos com "(?i)" e adicionando parênteses
    for termo in list_termos:
        # Adicionar "(?i)" para tornar a correspondência de termo insensível a maiúsculas e minúsculas
        string_modificado = string_modificado.replace(termo, f"((?i){termo})")

        # Adicionar parênteses em cada termo individual
        for i in termo.split('&'):
            string_modificado = string_modificado.replace(i, f"({i})")

    # Remover o caractere "&" da string modificada
    string_modificado = string_modificado.replace('&', '')

    # Retornar a string modificada
    return string_modificado


def converte_negativa_regex(termos):
    return "Rosangela e recebeu e indevida ((?!cobrança).)*$"


def traduz_regex(termo):
    """Função que traduz conectivos para expressões regex
        Página para exemplo dos conectivos ==>>  https://scon.stj.jus.br/SCON/

        Testar as regex https://regex101.com/
    """
    # TODO melhora as expressões "and" e "ou" as duas são muito parecidas
    dicionario = {"$": r"\w*", " OU ": "|"}
    termo = converte_and_regex(termo)

    for origem, regex in dicionario.items():
        termo = termo.replace(origem, regex)

    return termo


def transforma_em_regex(itemfiltro):
    if itemfiltro.regex:
        # return '(%s)' % itemfiltro.termos
        return f'({itemfiltro.termos})'
    else:
        # return '(%s)' % re.escape(traduz_regex(itemfiltro.termos))
        # Após alterações nos sistemas, todos os termos deveram ser tratados como regex
        return traduz_regex(itemfiltro.termos)


def montar_estrutura_filtro(m_filtro, serializavel=False):
    retorno = []
    for classe in m_filtro.classefiltro_set.all():
        pre_classe = {
            "nome": None,
            "classe": "" if serializavel else classe,
            "parametros": {
                "regex": [],
                "regex_reforco": None,
                "regex_exclusao": None,
                "regex_invalidacao": None,
                "coadunadas": None
            }
        }

        pre_classe['nome'] = slugify(classe.nome).replace('-', '_')
        pre_classe['parametros']['regex'] = list(map(
            transforma_em_regex,
            filter(
                lambda x: x.tipo == '1',
                classe.itemfiltro_set.all())))
        pre_classe['parametros']['regex_reforco'] = list(map(
            transforma_em_regex,
            filter(
                lambda x: x.tipo == '2',
                classe.itemfiltro_set.all())))
        pre_classe['parametros']['regex_exclusao'] = list(map(
            transforma_em_regex,
            filter(
                lambda x: x.tipo == '3',
                classe.itemfiltro_set.all())))
        pre_classe['parametros']['regex_invalidacao'] = list(map(
            transforma_em_regex,
            filter(
                lambda x: x.tipo == '4',
                classe.itemfiltro_set.all())))
        pre_classe['parametros']['coadunadas'] = list(map(
            transforma_em_regex,
            filter(
                lambda x: x.tipo == '5',
                classe.itemfiltro_set.all())))

        retorno.append(pre_classe)

    return retorno


def preparar_classificadores(estrutura):
    return [
        constroi_classificador_dinamica(item['nome'], item['parametros'])
        for item in estrutura
    ]


def obtem_classe(classificacao, estrutura):
    return next(
        filter(
            lambda x: x['nome'] == classificacao[
                'classificacao'].__class__.__name__,
            estrutura
        )
    )["classe"]
