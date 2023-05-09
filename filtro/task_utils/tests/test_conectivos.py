from django.test import TestCase
from filtro.task_utils.functions import traduz_regex, converte_and_regex, converte_negativa_regex


class TestTraduzRegex(TestCase):
    def test_traduz_regex(self):
        termo = 'cobran$a$ indevid$'
        expeted = "cobran\w*a\w* indevid\w*"
        self.assertEqual(traduz_regex(termo), expeted)

#
# @pytest.mark.test_regex  # para rodar o "mark" especifico - pytest -v -m test_regex
# def test_traduz_regex():
#     termo = 'cobran$a$ indevid$'
#     expeted = "cobran\w*a\w* indevid\w*"
#     assert traduz_regex(termo) == expeted
#
#     termos = "cobran$a$ OU indevid$ OU $osangela"
#     resultado_esperado = "cobran\w*a\w*|indevid\w*|\w*osangela"
#     assert traduz_regex(termos) == resultado_esperado
#
#     termo = "cobran$a$ e indevid$ e recebeu"
#     resultado_esperado = r"(cobran\w*a\w*|indevid\w*|recebeu)"
#     assert traduz_regex(termo) == resultado_esperado
#
#     termo = "valor atualizado do teto do benef$cio do INSS"
#     resultado_esperado = r"valor atualizado do teto do benef\w*cio do INSS"
#     assert traduz_regex(termo) == resultado_esperado
#
#
# def test_converte_and_regex():
#     s = "indevid$ OU $osangela OU cobran$a$ e indevid$ e recebeu OU A$$O e PEDIDO$ E PAGOU"
#     t = converte_and_regex(s)
#     print('\n', t, 50 * '*')
#     assert t == "indevid$ OU $osangela OU (cobran$a$|indevid$|recebeu) OU (A$$O|PEDIDO$|PAGOU)"
#
#     termos = "cobran$a$ e indevid$"
#     resultado_esperado = "(cobran$a$|indevid$)"
#     assert converte_and_regex(termos) == resultado_esperado
#
#     termos = "cobran$a$ e indevid$ e recebeu"
#     resultado_esperado = "(cobran$a$|indevid$|recebeu)"
#     assert converte_and_regex(termos) == resultado_esperado
#
#     termos = "COBRAN$A$|INDEVID$|RECEBEU"
#     resultado_esperado = "(COBRAN$A$|INDEVID$|RECEBEU)"
#     assert converte_and_regex(termos) == resultado_esperado
#
#
# def test_converte_negativo_regex():
#     """Deve converte o caracter Jurisprudência 'NÃO/não para ((?!...).)*$"""
#     Texto = """História 1:
#                 Lucas acabou de estacionar seu carro no estacionamento do supermercado. Ao retornar, encontrou seu carro
#                 arrombado e alguns pertences furtados. O segurança do estacionamento informou que havia ocorrido um
#                 furto recentemente em frente ao supermercado, mas as câmeras de segurança não captaram o ladrão.
#
#                História 2:
#                 Camila chegou ao estacionamento do shopping e foi surpreendida ao notar que seu carro não estava no
#                 lugar onde havia estacionado. Ao procurar ajuda na administração, descobriu que o estacionamento havia
#                 sido alvo de um furto durante a madrugada. Os ladrões levaram diversos veículos e ainda não haviam sido
#                 identificados pela polícia.
#
#                História 3:
#                 Felipe e sua esposa estacionaram o carro no estacionamento do supermercado e foram às compras.
#                 Ao retornar, perceberam que a janela do carro havia sido quebrada e alguns objetos furtados.
#                 Ao verificar as câmeras de segurança, descobriram que os ladrões haviam agido rapidamente e fugido em
#                 um carro que estava estacionado a quatro vagas de distância. As imagens foram entregues à polícia
#                 para investigação."""
#
#     # (furto|estacionamento)((?!supermercado).)*$
#
#     termos = "Rosangela e recebeu e indevida não cobrança"
#     resultado_esperado = "Rosangela e recebeu e indevida ((?!cobrança).)*$"
#     assert converte_negativa_regex(termos) == resultado_esperado
