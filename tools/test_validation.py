"""Regression checks for the real manuscript defects found during review."""
import unittest
from validate import inspect_math


class MathematicalMarkupTests(unittest.TestCase):
    def problems(self, text):
        issues = []
        inspect_math(text, 'fixture', issues)
        return issues

    def test_extra_closing_backslash_detected(self):
        self.assertTrue(self.problems(r'\(S_\alpha\\)'))

    def test_mismatched_or_unclosed_delimiters_detected(self):
        self.assertTrue(self.problems(r'\(x\]'))
        self.assertTrue(self.problems(r'\[x'))

    def test_raw_html_comparison_detected(self):
        self.assertTrue(self.problems(r'\(d>0\)'))
        self.assertFalse(self.problems(r'\(d\gt0\)'))

    def test_latex_escaped_braces_and_matrix_are_valid(self):
        self.assertFalse(self.problems(r'\[\{x\}\quad\begin{pmatrix}1&0\\0&1\end{pmatrix}\]'))

    def test_control_character_detected(self):
        self.assertTrue(self.problems('formula ' + chr(8) + 'eta'))


if __name__ == '__main__':
    unittest.main()
