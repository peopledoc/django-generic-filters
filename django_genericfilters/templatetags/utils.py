"""Template tag library.

Provides one template tag: "check_class".

Example:

.. code-block:: Django

    {% load utils %}

    {% if form.field|is_checkbox %}

"""

from django import template

register = template.Library()


@register.filter
def is_checkbox(form_field):
    return form_field.field.widget.__class__.__name__ == 'CheckboxInput'
