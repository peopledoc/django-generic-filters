import urllib

import factory
from django import forms
from django.db import models
from django.http import QueryDict
from django.test import RequestFactory, TestCase
from django.utils.datastructures import MultiValueDict

from django_genericfilters import views
from django_genericfilters.forms import FilteredForm


def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``

    See also: https://code.djangoproject.com/ticket/20456

    """

    view.request = request
    view.args = args
    view.kwargs = kwargs

    return view


class People(models.Model):
    """
    define a parent model
    """

    name = models.CharField(max_length=250)


class Status(models.Model):
    """
    define a dummy status model
    """

    name = models.CharField(max_length=250)


class Something(models.Model):
    """
    Define a dummy model for this test case
    """

    people = models.ForeignKey(People, on_delete=models.CASCADE)
    city = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    organization = models.CharField(max_length=250)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)


class StatusFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = Status


class PeopleFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = People


class SomethingFactory(factory.django.DjangoModelFactory):
    people = factory.SubFactory(PeopleFactory)
    status = factory.SubFactory(StatusFactory)
    city = factory.Faker("city")
    country = factory.Faker("country")
    organization = factory.Faker("company")

    class Meta:
        model = Something


class FilteredViewTestCase(TestCase):
    class Form(FilteredForm):

        city = forms.ChoiceField(
            label="city", required=False, choices=(("N", "Nantes"), ("P", "Paris"))
        )

        country = forms.ChoiceField(
            label="country",
            required=False,
            choices=(("F", "France"), ("P", "Portugal")),
        )

        people = forms.ChoiceField(
            label="people", required=False, choices=(("S", "Some"), ("A", "Any"))
        )

        organization = forms.MultipleChoiceField(
            label="organization",
            required=False,
            choices=(("A", "A Team"), ("B", "B Team"), ("C", "C Team")),
        )

        parent = forms.ModelChoiceField(
            queryset=People.objects.all(), label="parent", required=False
        )

        status = forms.ModelMultipleChoiceField(
            label="status", required=False, queryset=Status.objects.all()
        )

        def get_order_by_choices(self):
            return (("city", "City"), ("country", "Country"))

    @classmethod
    def setUpTestData(cls):
        SomethingFactory.create_batch(20)

    def test_default_order_fallback_form_valid(self):
        """Queryset is unordered if no default_order or data (valid form)."""
        data = {"city": "N"}
        view = setup_view(
            views.FilteredListView(model=Something, form_class=self.Form),
            RequestFactory().get("/fake", data),
        )

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(list(queryset.query.order_by), [])

    def test_default_order_fallback_form_invalid(self):
        """Queryset is unordered if no default_order or data (invalid form)."""
        data = {"city": "fake"}
        view = setup_view(
            views.FilteredListView(model=Something, form_class=self.Form),
            RequestFactory().get("/fake", data),
        )

        view.form.is_valid()
        queryset = view.form_invalid(view.form)
        self.assertEqual(list(queryset.query.order_by), [])

    def test_default_order_fallback_form_empty(self):
        """Queryset is unordered if no default_order or data (empty form)."""
        request = RequestFactory().get("/fake")
        view = setup_view(
            views.FilteredListView(model=Something, form_class=self.Form), request
        )

        queryset = view.form_empty()
        self.assertEqual(list(queryset.query.order_by), [])

    def test_default_filter(self):
        """Test the default filter"""
        request = RequestFactory().get("/fake")
        view = setup_view(
            views.FilteredListView(
                model=Something,
                form_class=self.Form,
                default_filter={"is_active": "1", "page": "1"},
            ),
            request,
        )

        query_filter = urllib.parse.urlencode({"is_active": "1", "page": "1"})
        get_filter = view.get_form_kwargs()
        self.assertEqual(get_filter["data"], QueryDict(query_filter))

    def test_default_filter_submit(self):
        """Test the default filter submit"""
        data = {"city": "N"}
        request = RequestFactory().get("/fake", data)
        view = setup_view(
            views.FilteredListView(
                model=Something,
                form_class=self.Form,
                default_filter={"is_active": "1", "page": "1"},
            ),
            request,
        )

        query_filter = urllib.parse.urlencode(
            {"is_active": "1", "page": "1", "city": "N"}
        )
        get_filter = view.get_form_kwargs()
        self.assertEqual(get_filter["data"], QueryDict(query_filter))

    def test_default_order_form_valid(self):
        """Queryset is ordered by default_order when no order_by in request."""
        data = {"city": "N"}
        view = setup_view(
            views.FilteredListView(
                model=Something, form_class=self.Form, default_order="city"
            ),
            RequestFactory().get("/fake", data),
        )

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(list(queryset.query.order_by), ["city"])

    def test_default_order_form_invalid(self):
        """Queryset is ordered by default_order when no order_by in request
        and form is invalid."""
        data = {"city": "fake"}
        view = setup_view(
            views.FilteredListView(
                model=Something, form_class=self.Form, default_order="city"
            ),
            RequestFactory().get("/fake", data),
        )

        view.form.is_valid()
        queryset = view.form_invalid(view.form)
        self.assertEqual(list(queryset.query.order_by), ["city"])

    def test_default_order_form_empty(self):
        """Queryset is ordered by default_order when no order_by in request."""
        request = RequestFactory().get("/fake")
        view = setup_view(
            views.FilteredListView(
                model=Something, form_class=self.Form, default_order="city"
            ),
            request,
        )
        queryset = view.form_empty()
        self.assertEqual(list(queryset.query.order_by), ["city"])

    def test_default_order_reverse(self):
        """To test order reverse"""
        data = {"city": "N"}
        view = setup_view(
            views.FilteredListView(
                model=Something, form_class=self.Form, default_order="-city"
            ),
            RequestFactory().get("/fake", data),
        )

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(list(queryset.query.order_by), ["-city"])

    def test_default_order_in_request(self):
        """Test with order_by in data."""
        data = {"city": "N", "order_by": "city"}
        view = setup_view(
            views.FilteredListView(
                model=Something, form_class=self.Form, default_order="-city"
            ),
            RequestFactory().get("/fake", data),
        )

        view.form.is_valid()
        queryset = view.form_valid(view.form)
        self.assertEqual(list(queryset.query.order_by), ["city"])

    def test_filtered_list_view(self):
        a = views.FilteredListView(
            filter_fields=["city"], form_class=self.Form, model=Something
        )

        b = views.FilteredListView(
            filter_fields=["city", "people"],
            qs_filter_fields={"people__name": "people"},
            form_class=self.Form,
            model=Something,
        )
        setattr(
            a,
            "request",
            type("obj", (object,), {"method": "GET", "GET": {"city": "N"}}),
        )

        setattr(
            b,
            "request",
            type("obj", (object,), {"method": "GET", "GET": {"people": "S"}}),
        )

        self.assertEqual({"city": "city"}, a.get_qs_filters())
        a.form.is_valid()
        self.assertIn(
            '"django_genericfilters_something"."city" = N',
            a.form_valid(a.form).query.__str__(),
        )

        self.assertEqual({"people__name": "people"}, b.get_qs_filters())
        b.form.is_valid()
        self.assertIn(
            '"django_genericfilters_people"."name" = S',
            b.form_valid(b.form).query.__str__(),
        )

    def test_filtered_list_view__none(self):
        """
        FIXED : None value understood as "IS NULL" filter instead of being ignored.
        """
        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "people__name": "people"},
            form_class=self.Form,
            model=Something,
        )

        data = {"city": "None", "people": "S"}
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()
        self.assertIn(
            '"django_genericfilters_people"."name" = S',
            str(view.form_valid(view.form).query),
        )

        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "people__name": "people"},
            form_class=self.Form,
            model=Something,
        )

        data = {"city": "N", "people": "None"}
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()
        self.assertIn(
            '"django_genericfilters_something"."city" = N',
            str(view.form_valid(view.form).query),
        )

    def test_filtered_list_view__multiplechoice(self):
        """
        FIXED : filtered fields has HiddenWidget widgets that cannot handle
                multiple values. Use Field.hidden_widget instead.
        """
        view = views.FilteredListView(
            filter_fields=["organization"], form_class=self.Form, model=Something
        )

        data = MultiValueDict({"organization": ["A"]})
        setup_view(view, RequestFactory().get("/fake", data))

        self.assertTrue(view.form.is_valid(), view.form.errors)
        self.assertIn(
            '"django_genericfilters_something"."organization" IN (A)',
            str(view.form_valid(view.form).query),
        )

        view = views.FilteredListView(
            filter_fields=["organization"], form_class=self.Form, model=Something
        )

        data = MultiValueDict({"organization": ["A", "C"]})
        setup_view(view, RequestFactory().get("/fake", data))
        self.assertTrue(view.form.is_valid())

    def test_filtered_list_view__multiplechoice__qs_filter_field(self):
        """
        FIXED : When using qs_filter_field, the behaviour changes because
                the HiddenWidget trick only works with filter_field
                attribute. But it compares a list with EQUAL operator
                instead of IN.
        """
        people = People.objects.create(name="fake")

        Something.objects.create(organization="A", people=people)
        Something.objects.create(organization="C", people=people)

        view = views.FilteredListView(
            qs_filter_fields={"organization": "organization"},
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"organization": ["A"]})
        setup_view(view, RequestFactory().get("/fake", data))

        self.assertTrue(view.form.is_valid(), view.form.errors)
        self.assertIn(
            '"django_genericfilters_something"."organization" IN (A)',
            str(view.form_valid(view.form).query),
        )
        self.assertEqual(1, view.form_valid(view.form).count())

        view = views.FilteredListView(
            qs_filter_fields={"organization": "organization"},
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"organization": ["A", "C"]})
        setup_view(view, RequestFactory().get("/fake", data))
        self.assertTrue(view.form.is_valid())
        self.assertEqual(2, view.form_valid(view.form).count())

    def test_filtered_list_view__modelchoice(self):
        peopleA = People.objects.create(name="fakeA")

        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "people": "parent"},
            form_class=self.Form,
            model=Something,
        )

        data = {"parent": peopleA.pk}
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()
        self.assertIn(
            '"django_genericfilters_something"."people_id" = %s' % (peopleA.pk,),
            str(view.form_valid(view.form).query),
        )

    def test_filtered_list_view__modelchoice__empty_queryset(self):
        """
        FIXED : Empty queryset in ModelChoiceField add "IS NULL" filters
                instead of ignore it.
        """
        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "people": "parent"},
            form_class=self.Form,
            model=Something,
        )

        data = {"city": "N", "parent": 1}
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()
        self.assertIn(
            '"django_genericfilters_something"."city" = N',
            str(view.form_valid(view.form).query),
        )

    def test_filtered_list_view__modelchoice__none(self):
        """
        FIXED : Empty queryset in ModelChoiceField add "IS NULL" filters
                instead of ignore it.
        """
        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "people": "parent"},
            form_class=self.Form,
            model=Something,
        )

        data = {"city": "N", "parent": "None"}
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()
        self.assertIn(
            '"django_genericfilters_something"."city" = N',
            str(view.form_valid(view.form).query),
        )

    def test_filtered_list_view__multiplemodelchoice(self):
        """
        FIXED : filtered fields has HiddenWidget widgets that cannot handle
                multiple values. Use Field.hidden_widget instead.
        """
        stateA = Status.objects.create(name="stateA")
        stateB = Status.objects.create(name="stateB")
        stateC = Status.objects.create(name="stateC")
        people = People.objects.create(name="fake")

        A = Something.objects.create(organization="A", people=people, status=stateA)
        B = Something.objects.create(organization="B", people=people, status=stateB)
        C = Something.objects.create(organization="C", people=people, status=stateB)
        Something.objects.create(organization="D", people=people, status=stateC)

        view = views.FilteredListView(
            filter_fields=["city", "status"],
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"status": [stateA.pk]})
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()

        self.assertIsInstance(
            view.form.fields["status"].widget, forms.MultipleHiddenInput
        )

        queryset = view.form_valid(view.form)
        self.assertIn("IN (%s)" % stateA.pk, str(queryset.query))
        self.assertEqual([A], list(queryset.all()))

        view = views.FilteredListView(
            filter_fields=["city", "status"],
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"status": [stateA.pk, stateB.pk]})
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()

        queryset = view.form_valid(view.form)
        self.assertEqual([A, B, C], list(queryset.all()))

    def test_filtered_list_view__multiplemodelchoice__qs_filter_field(self):
        stateA = Status.objects.create(name="stateA")
        stateB = Status.objects.create(name="stateB")
        stateC = Status.objects.create(name="stateC")
        people = People.objects.create(name="fake")

        A = Something.objects.create(organization="A", people=people, status=stateA)
        B = Something.objects.create(organization="B", people=people, status=stateB)
        C = Something.objects.create(organization="C", people=people, status=stateB)
        Something.objects.create(organization="D", people=people, status=stateC)

        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "status": "status"},
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"status": [stateA.pk]})
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()

        self.assertIsInstance(view.form.fields["status"].widget, forms.SelectMultiple)

        queryset = view.form_valid(view.form)
        self.assertIn("IN (%s)" % stateA.pk, str(queryset.query))
        self.assertEqual([A], list(queryset))

        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "status": "status"},
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"status": [stateA.pk, stateB.pk]})
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()

        queryset = view.form_valid(view.form)
        self.assertEqual([A, B, C], list(queryset))

    def test_filtered_list_view__multiplemodelchoice__invalid_id(self):
        """
        FIXED : Invalid id in MultipleModelChoiceField generate a None
                value and add "IS NULL" filter instead of ignore it.
        """
        Status.objects.create(name="stateA")
        Status.objects.create(name="stateB")

        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "status": "status"},
            form_class=self.Form,
            model=Something,
        )

        data = MultiValueDict({"status": [1001]})
        setup_view(view, RequestFactory().get("/fake", data))
        view.form.is_valid()
        # no filter at all
        self.assertNotIn("WHERE", str(view.form_valid(view.form).query))

    def test_filtered_list_view__multiplemodelchoice__none(self):
        """
        FIXED : Empty queryset in MultipleModelChoiceField is added as
                subrequest in filter and raises an sql error instead of
                ignore it.
        """
        people = People.objects.create(name="fake")

        statusA = Status.objects.create(name="stateA")
        statusB = Status.objects.create(name="stateB")

        Something.objects.create(organization="A", people=people, status=statusA)
        Something.objects.create(organization="C", people=people, status=statusB)

        view = views.FilteredListView(
            qs_filter_fields={"city": "city", "status": "status"},
            form_class=self.Form,
            model=Something,
        )

        setup_view(view, RequestFactory().get("/fake", {}))
        view.form.is_valid()
        # no filter at all
        self.assertNotIn("WHERE", str(view.form_valid(view.form).query))

    def test_is_form_submitted_method(self):
        """Is form submitted return True when the request method is GET."""
        request = RequestFactory().get("/fake", {"foo": "bar"})
        view = setup_view(views.FilteredListView(), request)
        assert view.is_form_submitted() is True

        request = RequestFactory().post("/fake", {"foo": "bar"})
        view = setup_view(views.FilteredListView(), request)
        assert view.is_form_submitted() is False

    def test_is_form_submitted_no_args(self):
        """Is form submitted return False when the queryset is empty."""
        request = RequestFactory().get("/fake")
        view = setup_view(views.FilteredListView(), request)
        assert view.is_form_submitted() is False
