import unittest

from django import forms
from django.db import models

from django_genericfilters import views
from django_genericfilters import forms as gf


class FilteredViewTestCase(unittest.TestCase):

    class QueryModel(models.Model):
        """
        Define a dummy model for this test case
        """
        city = models.CharField(max_length=250)


    class Form(gf.OrderFormMixin, gf.PaginationFormMixin,
               gf.QueryFormMixin, gf.FilteredForm):

        city = forms.ChoiceField(
            label= 'city', required=False,
            choices = (
                ("N", "Nantes"),
                ("P", "Paris")
                )
            )

        def get_order_by_choices(self):
            return (('last_name', 'Last Name'),
                    ('first_name', 'First Name'))

    def test_filtered_list_view(self):
        a = views.FilteredListView(filter_fields=['city'],
                             form_class=self.Form,
                             model=self.QueryModel)

        setattr(
            a,
            'request',
            type('obj', (object,),{"method": "GET" ,"GET":{"city":"N"}})
            )

        self.assertEqual({'city': 'city'}, a.get_qs_filters())
        a.form.is_valid()
        self.assertIn(
            'WHERE "tests_querymodel"."city" = N',
            a.form_valid(a.form).query.__str__()
            )
