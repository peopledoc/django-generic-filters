# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from .fields import *  # NOQA


class QueryFormMixin(forms.Form):
    query = forms.CharField(required=False)


class PaginationFormMixin(forms.Form):
    page = forms.IntegerField(label=_('page'),
                              required=False,
                              min_value=1,
                              initial=1)

    paginate_by = forms.IntegerField(label=_('paginate by'),
                                     required=False,
                                     initial=10,
                                     min_value=2,
                                     max_value=20)


class OrderFormMixin(forms.Form):
    order_by = forms.ChoiceField(label=_('order by'),
                                 required=False)

    order_reverse = forms.BooleanField(label=_('reverse order'),
                                       required=False,
                                       initial=False)

    def __init__(self, *args, **kwargs):
        super(OrderFormMixin, self).__init__(*args, **kwargs)
        self.fields['order_by'].choices = self.get_order_by_choices()

    def clean_order_by(self):
        if self['order_by'].html_name not in self.data:
            return self.initial.get(self['order_by'].html_name,
                                    self.fields['order_by'].initial)
        return self.cleaned_data['order_by']

    def get_order_by_choices(self):
        raise NotImplementedError(
            _("Don't forget to implements get_order_by_choices"))


class FilteredForm(forms.Form):
    """FilteredForm to add some magic."""

    __hide_fields = ['query', 'order_by', 'order_reverse',
                     'page', 'paginate_by']

    def __init__(self, *args, **kwargs):
        super(FilteredForm, self).__init__(*args, **kwargs)

        # Hide Hidden Fields
        for field in self.get_hidden_fields():
            if field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

        # It is not a model form so it doesn't work alone but I like this API.
        if hasattr(self, 'Meta'):
            for field in self.Meta.widgets:
                if field in self.fields:
                    self.fields[field].widget = self.Meta.widgets[field]

    def get_hidden_fields(self):
        hide_fields = self.__hide_fields
        if hasattr(self, 'hide_fields'):
            hide_fields += list(self.hide_fields)
        return hide_fields
