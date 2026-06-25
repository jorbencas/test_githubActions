"""Tests for ContentFilter class."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from downloadFile import ContentFilter


class TestFechaValida(unittest.TestCase):
    def test_valida(self):
        self.assertTrue(ContentFilter.es_fecha_valida("hace 2 días"))
        self.assertTrue(ContentFilter.es_fecha_valida("hace 3 semanas"))

    def test_invalida(self):
        self.assertFalse(ContentFilter.es_fecha_valida("hace 1 año"))
        self.assertFalse(ContentFilter.es_fecha_valida("hace 2 months"))
        self.assertFalse(ContentFilter.es_fecha_valida("hace 6 meses"))


class TestKeywords(unittest.TestCase):
    def test_tech_match(self):
        self.assertTrue(ContentFilter.coincide_con_keywords("Nueva IA de OpenAI"))

    def test_beca_match(self):
        self.assertTrue(ContentFilter.coincide_con_keywords("Beca de formación en Python"))

    def test_no_match(self):
        self.assertFalse(ContentFilter.coincide_con_keywords("Receta de cocina"))

    def test_empty(self):
        self.assertFalse(ContentFilter.coincide_con_keywords(""))

    def test_case_insensitive(self):
        self.assertTrue(ContentFilter.coincide_con_keywords("INTELIGENCIA ARTIFICIAL"))


class TestEsBeca(unittest.TestCase):
    def test_beca(self):
        self.assertTrue(ContentFilter.es_beca("Beca completa para bootcamp"))

    def test_curso(self):
        self.assertTrue(ContentFilter.es_beca("Curso gratis de Machine Learning"))

    def test_subvencion(self):
        self.assertTrue(ContentFilter.es_beca("Subvención para startups"))

    def test_taller(self):
        self.assertTrue(ContentFilter.es_beca("Taller de programación"))

    def test_no_beca(self):
        self.assertFalse(ContentFilter.es_beca("Oferta de trabajo senior"))

    def test_empty(self):
        self.assertFalse(ContentFilter.es_beca(""))

    def test_uppercase(self):
        self.assertTrue(ContentFilter.es_beca("BECA"))


class TestEsReto(unittest.TestCase):
    def test_reto(self):
        self.assertTrue(ContentFilter.es_reto("Nuevo reto de programación"))

    def test_challenge(self):
        self.assertTrue(ContentFilter.es_reto("Challenge semanal de algoritmos"))

    def test_desafio(self):
        self.assertTrue(ContentFilter.es_reto("Desafío de código abierto"))

    def test_no_reto(self):
        self.assertFalse(ContentFilter.es_reto("Noticia sobre Python"))

    def test_empty(self):
        self.assertFalse(ContentFilter.es_reto(""))

    def test_uppercase(self):
        self.assertTrue(ContentFilter.es_reto("RETO"))


if __name__ == "__main__":
    unittest.main()
