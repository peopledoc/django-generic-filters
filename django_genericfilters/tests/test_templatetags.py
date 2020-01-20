import unittest

from django import forms
from django.template.base import TOKEN_TEXT, Parser, Token, Variable

import mock

from django_genericfilters.templatetags.updateurl import (
    token_kwargs, token_value, tag_update_query_string, update_query_string
)
from django_genericfilters.templatetags.utils import is_checkbox


class TemplateTagTestCase(unittest.TestCase):
    def test_token_value(self):
        parser = Parser('')
        self.assertEqual(token_value('"A"', parser), 'A')
        var = token_value('a', parser).var
        self.assertTrue(isinstance(var, Variable))

    def test_token_kwargs(self):
        parser = Parser('')
        self.assertEqual(token_kwargs([], parser), {})
        bits = ['a="A"']
        token_kwargs(bits, parser)
        self.assertEqual(bits, [])
        bits = ['a="A"', 'invalid']
        token_kwargs(bits, parser)
        self.assertEqual(bits, ['invalid'])

    def test_update_query_string(self):
        self.assertEqual(
            update_query_string('/foo/?bar=baz', {'bar': 'updated'}),
            '/foo/?bar=updated')
        self.assertEqual(
            update_query_string('/foo/?bar=baz', {'bar': 'updated'}),
            '/foo/?bar=updated')
        self.assertEqual(
            update_query_string('/foo/', {'bar': 'created'}),
            '/foo/?bar=created')

    def test_tag_update_query_string(self):
        request = mock.Mock()
        request.get_full_path = mock.Mock(return_value='/fake')
        parser = Parser('')
        token = Token(TOKEN_TEXT, 'tag with "page"="2"')
        node = tag_update_query_string(parser, token)
        self.assertEqual(
            node.render({'request': request}),
            u'/fake?page=2')
        token = Token(TOKEN_TEXT, 'tag with page=num_page')
        node = tag_update_query_string(parser, token)
        self.assertEqual(
            node.render({'request': request, 'page': 'page', 'num_page': 2}),
            u'/fake?page=2')

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
