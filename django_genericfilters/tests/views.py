import unittest
import sys
import urllib

from django import forms
from django.db import models
from django.http import QueryDict

from django_genericfilters import views
from django_genericfilters.forms import FilteredForm

from django.test import RequestFactory


def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    See also: https://code.djangoproject.com/ticket/20456

    """

    view.request = request
    view.args = args
    view.kwargs = kwargs

    return view


class ParentModel(models.Model):
    """
    define a parent model
    """
    name = models.CharField(max_length=250)


class FilteredViewTestCase(unittest.TestCase):

    def assertIn(self, a, b, msg=None):
        if sys.version_info[:2] == (2, 6):
            # for 2.6 compatibility
            if a not in b:
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

    def test_default_order_fallback_form_valid(self):
        """Queryset is unordered if no default_order or data (valid form)."""
        data = {"city": "N"}
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel, form_class=self.Form),
            RequestFactory().get('/fake', data))

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(queryset.query.order_by, [])

    def test_default_order_fallback_form_invalid(self):
        """Queryset is unordered if no default_order or data (invalid form)."""
        data = {"city": "fake"}
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel, form_class=self.Form),
            RequestFactory().get('/fake', data))

        view.form.is_valid()
        queryset = view.form_invalid(view.form)
        self.assertEqual(queryset.query.order_by, [])

    def test_default_order_fallback_form_empty(self):
        """Queryset is unordered if no default_order or data (empty form)."""
        request = RequestFactory().get('/fake')
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel, form_class=self.Form),
            request)

        queryset = view.form_empty()
        self.assertEqual(queryset.query.order_by, [])

    def test_default_filter(self):
        """Test the default filter"""
        request = RequestFactory().get('/fake')
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel, form_class=self.Form,
                default_filter={'is_active': '1', 'page': '1'}),
            request)

        query_filter = urllib.urlencode({'is_active': '1', 'page': '1'})
        get_filter = view.get_form_kwargs()
        self.assertEqual(get_filter['data'], QueryDict(query_filter))

        def test_default_filter_submit(self):
            """Test the default filter submit"""
            data = {"city": "N"}
            request = RequestFactory().get('/fake', data)
            view = setup_view(
                views.FilteredListView(
                    model=self.QueryModel, form_class=self.Form,
                    default_filter={'is_active': '1', 'page': '1'}),
                request)

            query_filter = urllib.urlencode({
                'is_active': '1', 'page': '1', 'city': 'N'})
            get_filter = view.get_form_kwargs()
            self.assertEqual(get_filter['data'], QueryDict(query_filter))

    def test_default_order_form_valid(self):
        """Queryset is ordered by default_order when no order_by in request."""
        data = {"city": "N"}
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel,
                form_class=self.Form,
                default_order='last_name'),
            RequestFactory().get('/fake', data))

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(queryset.query.order_by, ['last_name'])

    def test_default_order_form_invalid(self):
        """Queryset is ordered by default_order when no order_by in request
        and form is invalid."""
        data = {"city": "fake"}
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel,
                form_class=self.Form,
                default_order='last_name'),
            RequestFactory().get('/fake', data))

        view.form.is_valid()
        queryset = view.form_invalid(view.form)
        self.assertEqual(queryset.query.order_by, ['last_name'])

    def test_default_order_form_empty(self):
        """Queryset is ordered by default_order when no order_by in request."""
        request = RequestFactory().get('/fake')
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel,
                form_class=self.Form,
                default_order='last_name'),
            request)

        queryset = view.form_empty()
        self.assertEqual(queryset.query.order_by, ['last_name'])

    def test_default_order_reverse(self):
        """To test order reverse"""
        data = {"city": "N"}
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel,
                form_class=self.Form,
                default_order='-last_name'),
            RequestFactory().get('/fake', data))

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(queryset.query.order_by, ['-last_name'])

    def test_default_order_in_request(self):
        """Test with order_by in data."""
        data = {"city": "N", "order_by": "last_name"}
        view = setup_view(
            views.FilteredListView(
                model=self.QueryModel,
                form_class=self.Form,
                default_order='-last_name'),
            RequestFactory().get('/fake', data))

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(queryset.query.order_by, ['last_name'])

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

    def test_is_form_submitted_method(self):
        """Is form submitted return True when the request method is GET."""
        request = RequestFactory().get('/fake', {"foo": "bar"})
        view = setup_view(views.FilteredListView(), request)
        assert view.is_form_submitted() is True

        request = RequestFactory().post('/fake', {"foo": "bar"})
        view = setup_view(views.FilteredListView(), request)
        assert view.is_form_submitted() is False

    def test_is_form_submitted_no_args(self):
        """Is form submitted return False when the queryset is empty."""
        request = RequestFactory().get('/fake')
        view = setup_view(views.FilteredListView(), request)
        assert view.is_form_submitted() is False
