import unittest
import sys
from django import forms
from django.db import models

from django_genericfilters import views
from django_genericfilters.forms import FilteredForm


class ParentModel(models.Model):
    """
    define a parent model
    """
    name = models.CharField(max_length=250)


class FilteredViewTestCase(unittest.TestCase):

    def assertIn(self, a, b, msg=None):
        if sys.version_info[:2] == (2, 6):
            # for 2.6 compatibility
            if not a in b:
                self.fail("%s is not in %b" % (repr(a), repr(b)))
        else:
            super(FilteredViewTestCase, self).assertIn(a, b, msg=msg)

    class QueryModel(models.Model):
        """
        Define a dummy model for this test case
        """
        people = models.ForeignKey(ParentModel)
        city = models.CharField(max_length=250)
        country = models.CharField(max_length=250)

    class Form(FilteredForm):

        city = forms.ChoiceField(
            label='city', required=False,
            choices=(
                ("N", "Nantes"),
                ("P", "Paris")
            )
        )

        country = forms.ChoiceField(
            label='country', required=False,
            choices=(
                ("F", "France"),
                ("P", "Portugal")
            )
        )

        people = forms.ChoiceField(
            label='people', required=False,
            choices=(
                ("S", "Some"),
                ("A", "Any")
            )
        )

        def get_order_by_choices(self):
            return (('last_name', 'Last Name'),
                    ('first_name', 'First Name'))

    def test_filtered_list_view(self):
        a = views.FilteredListView(filter_fields=['city'],
                                   form_class=self.Form,
                                   model=self.QueryModel)

        b = views.FilteredListView(filter_fields=['city', 'people'],
                                   qs_filter_fields={'people__name': 'people'},
                                   form_class=self.Form,
                                   model=self.QueryModel)
        setattr(
            a,
            'request',
            type('obj', (object, ), {"method": "GET", "GET": {"city": "N"}})
        )

        setattr(
            b,
            'request',
            type('obj', (object, ), {"method": "GET", "GET": {"people": "S"}})
        )

        self.assertEqual({'city': 'city'}, a.get_qs_filters())
        a.form.is_valid()
        self.assertIn(
            'WHERE "tests_querymodel"."city" = N',
            a.form_valid(a.form).query.__str__()
        )

        self.assertEqual({'people__name': 'people'}, b.get_qs_filters())
        b.form.is_valid()
        self.assertIn(
            'WHERE "tests_parentmodel"."name" = S ',
            b.form_valid(b.form).query.__str__()
        )
