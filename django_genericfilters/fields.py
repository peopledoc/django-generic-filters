# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class ChoiceField(forms.ChoiceField):

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('required', False)

        if 'choices' not in kwargs:
            kwargs['choices'] = (
                ('yes', kwargs.get('label', _('Yes'))),
                ('no', _('No %(label)s') % {'label': kwargs.get('label', '')}))
        super(ChoiceField, self).__init__(*args, **kwargs)
