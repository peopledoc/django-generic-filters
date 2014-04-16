# -*- coding: utf-8 -*-
import unittest

from django import forms

from django_genericfilters import forms as gf


class FormTestCase(unittest.TestCase):

    def test_query_form_mixin(self):
        class Form(gf.QueryFormMixin, forms.Form):
            pass

        form = Form()

        self.assertTrue('query' in form.fields)

    def test_order_form_mixin(self):
        def get_order_by_choices():
            return (('last_name', 'Last Name'),
                    ('first_name', 'First Name'))

        class Form(gf.OrderFormMixin, forms.Form):
            def get_order_by_choices(self):
                return get_order_by_choices()

        form = Form()

        self.assertTrue('order_by' in form.fields)
        self.assertTrue('order_reverse' in form.fields)

        self.assertEqual(form.fields['order_by'].choices,
                         list(get_order_by_choices()))

    def test_get_order_by_choices_not_implemented(self):
        class Form(gf.OrderFormMixin):
            pass

        self.assertRaises(NotImplementedError, Form)


class FilteredFormTestCase(unittest.TestCase):

    # Define a form class for this test case
    class Form(gf.FilteredForm):

        def get_order_by_choices(self):
            return (('last_name', 'Last Name'),
                    ('first_name', 'First Name'))

    def test_empty_form_bound(self):
        form = self.Form(data={}, initial={"order_by": 'last_name'})
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['order_by'], 'last_name')

    def test_form_order_by_bound(self):
        form = self.Form(data={'order_by': 'first_name', 'order_reverse': 0},
                         initial={"order_by": 'last_name'})
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['order_by'], 'first_name')

    def test_filtered_form(self):
        form = self.Form()

        self.assertEqual(str(type(form.fields['query'].widget)),
                         "<class 'django.forms.widgets.HiddenInput'>")

        self.assertEqual(str(type(form.fields['order_by'].widget)),
                         "<class 'django.forms.widgets.HiddenInput'>")

        self.assertEqual(str(type(form.fields['order_reverse'].widget)),
                         "<class 'django.forms.widgets.HiddenInput'>")
