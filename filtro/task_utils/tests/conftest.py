import pytest
from dj_database_url import parse as db_url
from decouple import config, Csv
from unipath import Path
from django.conf import settings

BASE_DIR = Path(__file__).parent.parent


@pytest.fixture(scope='session')
def django_db_setup():
    # settings.DATABASES['default']: config('DATABASE_URL',
    #                                       default='sqlite:///' + BASE_DIR.child('dominio.sqlite3'),
    #                                       cast=db_url)

    settings.DATABASES['proc_base'] = config('DATABASE_PROCESSO',
                                             default='sqlite:///' + BASE_DIR.child('proc_base.sqlite3'),
                                             cast=db_url
                                             ),
