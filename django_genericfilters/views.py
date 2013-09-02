# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.utils.translation import ugettext_lazy as _

from bunch import Bunch


def str2bool(v):
    return v.lower() in ('1', 'true', 'yes', 'y', 't')


def is_filter(value, form):
    return bool(value in form.cleaned_data and form.cleaned_data[value])


class FilteredListView(FormMixin, ListView):
    """Base view where GET form is used to filter queryset."""
    initial = {'page': 1, 'paginate_by': 10}

    def is_form_submitted(self):
        return self.request.method == 'GET' and self.request.GET

    def get_initial(self):
        kwargs = super(FilteredListView, self).get_initial()
        if hasattr(self, 'default_order'):
            order_by = self.default_order
            order_reverse = 0
            if order_by.startswith('-'):
                order_by = order_by[1:]
                order_reverse = 1
            kwargs.update({'order_by': order_by,
                           'order_reverse': order_reverse})
        return kwargs

    def get_form_kwargs(self):
        """Read GET data to return keyword arguments for the form."""
        kwargs = {'initial': self.get_initial()}
        if self.is_form_submitted():
            kwargs.update({'data': self.request.GET})
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

    def form_valid(self, form):
        """Return queryset with form."""
        # Get default queryset from ListView parameters (queryset, model, ...)
        queryset = self.__get_queryset()

        # Handle PaginateFormMixin
        if is_filter('paginate_by', form):
            self.paginate_by = form.cleaned_data['paginate_by']

        # Handle QueryFormMixin
        if is_filter('query', form):
            query = form.cleaned_data['query']
            filters = None
            for f in self.search_fields:
                q = Q(**{f + '__icontains': query})
                filters = filters | q if filters else q
            if filters:
                queryset = queryset.filter(filters)

        # Handle OrderFormMixin
        if is_filter('order_by', form):
            order_field = form.cleaned_data['order_by']
            queryset = queryset.order_by(order_field)
        if is_filter('order_reverse', form):
            queryset = queryset.reverse()

        # Handle distinct for Join in some Querysets
        queryset = queryset.distinct()
        return queryset

    def form_invalid(self, form):
        """Return default queryset."""
        queryset = self.__get_queryset()
        if self.order_by_list:
            queryset = queryset.order_by(*self.order_by_list)
        return queryset

    @property
    def form(self):
        """Return form."""
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
        kwargs.setdefault('page', 1)
        kwargs = ListView.get_context_data(self, **kwargs)
        kwargs['form'] = self.form
        kwargs['filters'] = self.get_filters()
        return kwargs

    def get_filters(self):
        """Convert some ChoiceField in a list of choices in the template."""
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
                if not self.form.fields[field].required:
                    all_choice = Bunch(value='', label=_('All'),
                                       is_selected=(not selected))
                    new_filter.choices.insert(0, all_choice)
                filters.append(new_filter)

        return filters
