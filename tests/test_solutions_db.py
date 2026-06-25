"""Tests for solutions_db module."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from solutions_db import lookup, generate_generic, _normalize_key, SOLUTIONS


class TestLookup(unittest.TestCase):
    def test_known_challenge_returns_solution(self):
        sol = lookup("suma de digitos", "python")
        self.assertIsNotNone(sol)
        self.assertTrue(sol["descripcion"])
        self.assertTrue(sol["codigo"])
        self.assertTrue(sol["big_o_time"])
        self.assertTrue(sol["big_o_space"])
        self.assertTrue(sol["test_cases"])

    def test_known_challenge_all_languages(self):
        langs = ["python", "javascript", "typescript", "go", "rust", "java",
                 "csharp", "kotlin", "swift", "php", "ruby", "dart"]
        for lang in langs:
            sol = lookup("par o impar", lang)
            self.assertIsNotNone(sol, f"Missing solution for {lang}")
            self.assertTrue(sol["codigo"], f"Empty code for {lang}")

    def test_unknown_challenge_returns_none(self):
        sol = lookup("xyz-not-a-real-challenge-42", "python")
        self.assertIsNone(sol)

    def test_lookup_fibonacci(self):
        sol = lookup("fibonacci recursivo", "python")
        self.assertIsNotNone(sol)
        self.assertIn("fib", sol["codigo"].lower())
        self.assertEqual(sol["big_o_time"], "O(2^n) (O(n) con memoización)")

    def test_lookup_palindrome(self):
        sol = lookup("detector de palindromos", "javascript")
        self.assertIsNotNone(sol)
        self.assertEqual(sol["big_o_time"], "O(n)")
        self.assertEqual(sol["big_o_space"], "O(n)")

    def test_lookup_all_slugs(self):
        known = ["suma-de-digitos", "par-o-impar", "invertir-palabra",
                 "fibonacci-recursivo", "detector-de-palindromos"]
        for slug in known:
            sol = lookup(slug.replace("-", " "), "python")
            self.assertIsNotNone(sol, f"Could not find {slug}")


class TestGenerateGeneric(unittest.TestCase):
    def test_generic_generator_returns_valid_dict(self):
        sol = generate_generic("invertir lista", "python")
        self.assertEqual(sol["titulo"], "invertir lista")
        self.assertTrue(sol["codigo"])
        self.assertEqual(sol["big_o_time"], "O(n)")
        self.assertEqual(sol["big_o_space"], "O(n)")
        self.assertEqual(sol["dificultad"], "Intermedio")

    def test_generic_generator_invalid_lang(self):
        sol = generate_generic("test", "brainfuck")
        self.assertIsNotNone(sol)
        self.assertTrue(sol["codigo"])

    def test_generic_generator_with_description(self):
        sol = generate_generic("test", "python", descripcion="Custom desc")
        self.assertIn("Custom desc", sol["descripcion"])


class TestNormalizeKey(unittest.TestCase):
    def test_par_o_impar(self):
        self.assertEqual(_normalize_key("Par o Impar"), "par-o-impar")

    def test_special_chars(self):
        self.assertEqual(_normalize_key("¡Hola, Mundo!"), "hola-mundo")

    def test_spaces(self):
        self.assertEqual(_normalize_key("  spaces   "), "spaces")


class TestSolutionsIntegrity(unittest.TestCase):
    def test_curated_have_full_fields(self):
        curated = {"suma-de-digitos", "par-o-impar", "invertir-palabra",
                   "fibonacci-recursivo", "detector-de-palindromos"}
        for slug in curated:
            self.assertIn(slug, SOLUTIONS, f"{slug} missing from merged SOLUTIONS")
            data = SOLUTIONS[slug]
            self.assertIn("big_o_time", data, f"{slug} missing big_o_time")
            self.assertIn("big_o_space", data, f"{slug} missing big_o_space")
            self.assertIn("test_cases", data, f"{slug} missing test_cases")

    def test_extended_have_basic_fields(self):
        self.assertGreater(len(SOLUTIONS), 10, "Should have merged solutions")
        for slug, data in SOLUTIONS.items():
            self.assertIn("desc", data, f"{slug} missing desc")
            self.assertIn("p1", data, f"{slug} missing p1")

    def test_curated_override_extended(self):
        sol = lookup("suma de digitos", "python")
        self.assertEqual(sol["big_o_time"], "O(log n)")

    def test_extended_lookup_by_slug(self):
        sol = lookup("vocales en mayo", "python")
        self.assertIsNotNone(sol)
        self.assertTrue(sol["codigo"])

    def test_lookup_with_short_key(self):
        sol = lookup("validador de rango", "javascript")
        self.assertIsNotNone(sol)
        self.assertTrue(sol["codigo"])


if __name__ == "__main__":
    unittest.main()
