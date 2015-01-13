"""Template tag library.

Provides one template tag: "check_class".

Example:

.. code-block:: Django

{% load utils %}

{{ form.field.__class__.__name__ }}

"""

from django import template

register = template.Library()

@register.filter
def is_checkbox(form_field):
    # import ipdb; ipdb.set_trace()
    return form_field.field.widget.__class__.__name__ == 'CheckboxInput'
