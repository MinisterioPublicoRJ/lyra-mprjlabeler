from django.test import TestCase

from processos.models import ReusProcessosColetados


class TestPesquisaReu(TestCase):
    # min = ReusProcessosColetados.objects.using('proc_base').filter(pessoa_reu__unaccent__icontains='MINISTeRIO PuBLICO')
    min = ReusProcessosColetados.objects.using('proc_base').filter(pessoa_reu__unaccent__trigram_similar='MINISTeRIO PuBLICO')
    print(min.count())
