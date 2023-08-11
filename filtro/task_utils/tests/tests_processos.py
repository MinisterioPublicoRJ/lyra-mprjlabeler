import os
import pytest

os.environ['DJANGO_SETTINGS_MODULE'] = 'mprjlabeler.settings'

import django

django.setup()

from filtro.task_utils.obter_num_processo import obter_numeros_processos


# class TestsNumerosProcessos(TestCase):
# @pytest.fixture
@pytest.mark.django_db
def test_obter_numeros_processos():
    n_processos = obter_numeros_processos('MINISTERIO PUBLICO')

    assert len(n_processos) > 1
