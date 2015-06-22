# -*- coding: utf-8 -*-
from django import forms
from django.http import QueryDict
from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.utils.translation import ugettext_lazy as _

from bunch import Bunch


def is_filter(value, form):
    return bool(value in form.cleaned_data and form.cleaned_data[value])


class FilteredListView(FormMixin, ListView):
    """A Generic ListView used to filter and order objects."""
    default_order = None
    default_filter = None

    def is_form_submitted(self):
        """
        Return True if the form is already submited. False otherwise
        """
        return bool(self.request.method == 'GET' and self.request.GET)

    def get_initial(self):
        """
        add "order_by" and "order_reverse" to the initials.
        """
        kwargs = super(FilteredListView, self).get_initial()

        if self.default_order:
            order_by = self.default_order

            kwargs['order_by'] = order_by
            kwargs['order_reverse'] = order_by.startswith('-')

        return kwargs

    def get_form_kwargs(self):
        """Read GET data to return keyword arguments for the form."""
        kwargs = {'initial': self.get_initial()}
        data = QueryDict({}).copy()

        if self.default_filter:
            data.update(self.default_filter)

        if self.is_form_submitted():
            data.update(self.request.GET)

        kwargs.update({'data': data})

        return kwargs

    def __get_queryset(self):
        """Helper to get ListView default queryset."""
        return super(ListView, self).get_queryset()

    def get_queryset(self):
        """Return filtered queryset. Uses form_valid() or form_invalid()."""
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    def get_qs_filters(self):
        """
        retreive filters from "qs_filter_fields" or "filter_fields"
        and return them as a dict to be used by self.form_valid
        """

        filters = {}

        if hasattr(self, 'qs_filter_fields'):
            filters = self.qs_filter_fields

        elif hasattr(self, 'filter_fields'):
            for field in self.filter_fields:
                filters[field] = field

        return filters

    def form_valid(self, form):
        """
        The form_valid is reponsible for filtering and ordering the
        base queryset. It return a queryset.

        :param: `django.forms.Forms`
        :return: `django.db.models.query.QuerySet`
        """
        # Get default queryset from ListView parameters (queryset, model, ...)
        queryset = self.__get_queryset()

        # Handle QueryFormMixin
        if is_filter('query', form):
            query = form.cleaned_data['query']
            query_words = query.split()
            filters = None
            for f in self.search_fields:
                for word in query_words:
                    q = Q(**{f + '__icontains': word})
                    filters = filters | q if filters else q
            if filters:
                queryset = queryset.filter(filters)

        # Handle get_qs_filters
        filters = {}
        for k, v in self.get_qs_filters().iteritems():
            field = form.cleaned_data.get(v)
            if field and field != '-1':
                filters[k] = field

                # Get extra condition for a field to on the filters
                if hasattr(self, 'qs_filter_fields_conditions'):
                    try:
                        filter_fields_conditions = self.\
                            qs_filter_fields_conditions[k]
                    except KeyError:
                        filter_fields_conditions = {}

                    for key, value in filter_fields_conditions.iteritems():
                        filters[key] = value

        queryset = queryset.filter(**filters)

        # Handle OrderFormMixin
        if is_filter('order_by', form):
            order_field = form.cleaned_data['order_by']
            queryset = queryset.order_by(order_field)

        if is_filter('order_reverse', form):
            queryset = queryset.reverse()

        return queryset

    def form_invalid(self, form):
        """Return queryset when submitted form is invalid.

        Default implementation uses :meth:`form_empty`.

        :param: `django.forms.Forms`
        :return: `django.db.models.query.QuerySet`

        """
        return self.form_empty()

    def form_empty(self):
        """Return queryset used when form is not submitted."""
        queryset = self.__get_queryset()
        if self.default_order:
            queryset = queryset.order_by(self.default_order)

        return queryset

    @property
    def form(self):
        """
        guess the form to be used and hide the filter_fields in the template

        """
        try:
            return self._form
        except AttributeError:
            form_class = self.get_form_class()
            self._form = self.get_form(form_class)

            # Hide filter_fields
            if hasattr(self, 'filter_fields'):
                for field in self.filter_fields:
                    self._form.fields[field].widget = forms.HiddenInput()

            return self._form

    def get_context_data(self, **kwargs):
        """
        Add a list of filters and self.form to the context to be rendered by
        the view.
        """
        kwargs = ListView.get_context_data(self, **kwargs)
        kwargs['form'] = self.form
        kwargs['filters'] = self.get_filters()

        return kwargs

    def get_filters(self):
        """
        Convert some ChoiceField in a list of choices in the
        template.
        """
        filters = []

        if hasattr(self, 'filter_fields'):
            for field in self.filter_fields:
                new_filter = Bunch()
                new_filter.label = self.form.fields[field].label
                new_filter.name = field
                new_filter.choices = []
                selected = False
                for choice in self.form.fields[field].choices:
                    new_choice = Bunch()
                    new_choice.value = choice[0]
                    new_choice.label = choice[1]
                    if hasattr(self.form, 'cleaned_data') and \
                            field in self.form.cleaned_data:
                        # Get value for ModelChoiceField or ChoiceField
                        value = getattr(self.form.cleaned_data[field], 'pk',
                                        self.form.cleaned_data[field])
                        if value == choice[0]:
                            new_choice.is_selected = True
                            selected = True
                        else:
                            new_choice.is_selected = False
                    else:
                        new_choice.is_selected = False
                    new_filter.choices.append(new_choice)

                if not self.form.fields[field].required and \
                        not [c for c in new_filter.choices
                             if c.value == '-1' or c.value == '']:
                    all_choice = Bunch(value='', label=_('All'),
                                       is_selected=(not selected))
                    new_filter.choices.insert(0, all_choice)
                filters.append(new_filter)

        return filters
