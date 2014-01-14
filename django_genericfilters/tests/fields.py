# -*- coding: utf-8 -*-
import unittest

from django import forms
from django_genericfilters import forms as gf


class FieldTestCase(unittest.TestCase):

    def setUp(self):

        class Form(forms.Form):
            test = gf.ChoiceField(label='Test')

        self.form = Form()

    def test_filtered_choice_field_required(self):
        self.assertFalse(self.form.fields['test'].required)

    def test_filtered_choice_field_auto_choices(self):
        choices = self.form.fields['test'].choices

        self.assertEqual(choices[0][0], 'yes')
        self.assertEqual(choices[0][1], 'Test')

        self.assertEqual(choices[1][0], 'no')
        self.assertEqual(choices[1][1], 'No Test')
