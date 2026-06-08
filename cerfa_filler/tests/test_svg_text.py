from django.template import Context, Template
from django.test import SimpleTestCase

from cerfa_filler.templatetags.svg_text import svg_wrap


class SvgWrapFilterTest(SimpleTestCase):
    def test_svg_wrap_splits_long_text(self):
        text = "Un don en nature compose de plusieurs elements distincts"

        lines = svg_wrap(text, "120,12")

        self.assertGreater(len(lines), 1)
        self.assertEqual(" ".join(lines), text)

    def test_svg_wrap_keeps_empty_value_visible(self):
        self.assertEqual(svg_wrap("", "120,12"), ["-"])

    def test_svg_wrap_limits_lines(self):
        text = "Un deux trois quatre cinq six sept huit neuf dix onze douze"

        lines = svg_wrap(text, "55,12,2")

        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[-1].endswith("..."))

    def test_filter_can_be_loaded_in_template(self):
        rendered = Template(
            "{% load svg_text %}"
            "{% for line in value|svg_wrap:'120,12' %}"
            "{{ line }}|"
            "{% endfor %}"
        ).render(Context({"value": "Un texte assez long pour revenir"}))

        self.assertIn("|", rendered)
