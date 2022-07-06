import logging
import re
from classificador_lyra.regex import constroi_classificador_dinamica
from processostjrj.mni import consulta_processo, cria_cliente
from slugify import slugify
from filtro.models import Documento
from filtro.task_utils.iniciais import processar as processar_iniciais

logger = logging.getLogger(__name__)


def limpar_documentos(m_filtro):
    m_filtro.documento_set.all().delete()


def parse_documentos(m_filtro):
    m_filtro.arquivo_documentos.open(mode='r')
    retorno = m_filtro.arquivo_documentos.readlines()
    m_filtro.arquivo_documentos.close()
    return retorno


def download_processos(documentos, trazer_iniciais=False):
    cliente = cria_cliente()
    for numero in documentos:
        iniciais = []
        f_numero = numero.strip().zfill(20)
        if not numero:
            continue
        try:
            processo = consulta_processo(
                cliente,
                f_numero,
                movimentos=True,
                _value_1=[{"incluirCabecalho": True}]
            )
            if trazer_iniciais:
                iniciais = processar_iniciais(f_numero)

        except Exception as error:
            logger.error('Erro no download do processo %s' % numero, error)
            continue
        yield (numero, processo, iniciais)


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


def traduz_regex(termo):
    """Modulo que traduz conectivos para caracter regex
        Pagina para exemplo dos conectivos ==>>  https://scon.stj.jus.br/SCON/
    """
    dicionario = {"$": ".", "ou": "|"}
    for origem, regex in dicionario.items():
        termo = termo.replace(origem, regex)

    """
        Aqui eu testo se o ultimo caracter é '.' e troco por '\w*' que é mais cirúrgico.
        Pego a string(palavra), do começo ate a penúltima letra e troco a última letra por '\w*'.
        Não uso o replace que troca todos os '.' por '\w*'.  
    """
    if termos := ''.join(palavra[:-1] + "\w* " for palavra in termo.split() if palavra[-1] == "."):
        termo = termos.strip()

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
