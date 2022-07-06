from django.test import TestCase
from ..functions import traduz_regex

class Test(TestCase):
    def setUp(self) -> None:
        self.termo = 'cobran$a$ indevid$'

    def test_last_caracter(self):
        expeted = "cobran.a\w* indevid\w*"
        transled = traduz_regex(self.termo)

        self.assertEqual(expeted, transled)  # add assertion here
