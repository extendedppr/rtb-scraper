import os
from datetime import datetime

from unittest import TestCase

from rtb_scraper.utils import (
    clean_string,
    remove_brackets_and_contents,
    removeprefix,
    is_determination_or_tribunal,
    remove_double_spaces,
)


class UtilsTest(TestCase):

    def test_clean_string(self):
        self.assertEqual(clean_string(""), "")
        self.assertEqual(clean_string("  "), "")
        self.assertEqual(clean_string("  a   b     c  "), "a b c")
        self.assertEqual(clean_string(": CONTENT   CONTENT,"), "CONTENT CONTENT")
        self.assertEqual(clean_string("Something , here"), "Something, here")
        # self.assertEqual(clean_string('Something ,here'), 'Something, here')

    def test_remove_brackets_and_contents(self):
        self.assertEqual(remove_brackets_and_contents("a(b)1[c{d}]e"), "a1e")

    def test_remove_prefix(self):
        self.assertEqual(removeprefix("", ""), "")
        self.assertEqual(removeprefix("abcd", "abc"), "d")
        self.assertEqual(removeprefix("abcd", "wabc"), "abcd")

    def test_remove_double_spaces(self):
        self.assertEqual(remove_double_spaces("  a   b     c  "), " a b c ")
        self.assertEqual(remove_double_spaces(" a b c"), " a b c")
