import unittest

from django import forms
from django.template import Context, Template
from django.template.base import Parser, Variable
from django.test import RequestFactory

from django_genericfilters.templatetags.updateurl import (
    token_kwargs,
    token_value,
    update_query_string,
)
from django_genericfilters.templatetags.utils import is_checkbox


class TemplateTagTestCase(unittest.TestCase):
    def test_token_value(self):
        parser = Parser("")
        self.assertEqual(token_value('"A"', parser), "A")
        var = token_value("a", parser).var
        self.assertTrue(isinstance(var, Variable))

    def test_token_kwargs(self):
        parser = Parser("")
        self.assertEqual(token_kwargs([], parser), {})
        bits = ['a="A"']
        token_kwargs(bits, parser)
        self.assertEqual(bits, [])
        bits = ['a="A"', "invalid"]
        token_kwargs(bits, parser)
        self.assertEqual(bits, ["invalid"])

    def test_update_query_string(self):
        self.assertEqual(
            update_query_string("/foo/?bar=baz", {"bar": "updated"}),
            "/foo/?bar=updated",
        )
        self.assertEqual(
            update_query_string("/foo/?bar=baz", {"bar": "updated"}),
            "/foo/?bar=updated",
        )
        self.assertEqual(
            update_query_string("/foo/", {"bar": "created"}), "/foo/?bar=created"
        )

    def test_tag_update_query_string(self):
        template = Template(
            "{% load updateurl %}{% update_query_string with page=num_page %}"
        )
        self.assertEqual(
            template.render(
                Context(
                    {
                        "request": RequestFactory().get("/fake"),
                        "page": "page",
                        "num_page": 2,
                    }
                )
            ),
            u"/fake?page=2",
        )

    def test_is_checkbox(self):
        class MockForm(forms.Form):
            a = forms.CharField()
            b = forms.BooleanField()

        form = MockForm()

        boundfield_a, boundfield_b = form.visible_fields()

        self.assertEqual("a", boundfield_a.name)
        self.assertFalse(is_checkbox(boundfield_a))

        self.assertEqual("b", boundfield_b.name)
        self.assertTrue(is_checkbox(boundfield_b))
