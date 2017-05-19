"""Template tag library around URL transformations.

Provides one template tag: "update_query_string".

Example:

.. code-block:: Django

   {% load updateurl %}

   First example using strings:
   {% update_query_string with 'page'='2' %}

   Second example using variables (both sides of "=" can be variables):
   {% update_query_string with page=paginator.next_page %}

"""
import six
from six.moves import urllib

import re

from django import template
from django.template.base import FilterExpression
from django.utils.html import conditional_escape


register = template.Library()


def token_value(bits, parser):
    """Parse ``bits`` string and return string or variable (FilterExpression).

    """
    if bits[0] in ('"', "'"):  # Parse a string.
        if not (bits[0] == bits[-1] or len(bits) < 2):
            raise template.TemplateSyntaxError("Malformed argument %r" % bits)
        return bits[1:-1]
    else:  # Parse a variable.
        return FilterExpression(bits, parser)


def token_kwargs(bits, parser):
    """Return dictionary of keywords arguments from ``bits``.

    bits
      A list containing remainder of the token (split by spaces) that is to be
      checked for arguments. Valid arguments will be removed from this list.

    parser
      A template parser instance.

    There is no requirement for all remaining token ``bits`` to be keyword
    arguments, so the dictionary will be returned as soon as an invalid
    argument format is reached.

    .. note::

       This function is a fork of :py:func:`django.template.base.token_kwargs`
       that adds support for variables both sides of the "=" assignation
       operator.

    """
    if not bits:
        return {}
    kwarg_re = re.compile(r"(?P<key>.+)=(?P<value>.+)")
    kwargs = {}
    while bits:
        match = kwarg_re.match(bits[0])
        if not match or not match.group('key') or not match.group('value'):
            return kwargs
        key = token_value(match.group('key'), parser)
        value = token_value(match.group('value'), parser)
        kwargs[key] = value
        del bits[:1]
    return kwargs


def update_query_string(url, updates):
    """Update query string in ``url`` with ``updates``.

    """
    url_parts = list(urllib.parse.urlparse(str(url)))
    query_dict = urllib.parse.parse_qs(url_parts[4])
    query_dict.update(updates)
    query_string = urllib.parse.urlencode(query_dict, True)
    url_parts[4] = query_string
    return urllib.parse.urlunparse(url_parts)


class UpdateQueryStringNode(template.Node):
    def __init__(self, url=None, qs_updates={}):
        self.url = url
        self.qs_updates = qs_updates

    def render(self, context):
        if self.url is None:  # Fallback to current URL.
            request = context['request']
            url = request.get_full_path()
        else:
            url = self.url
        try:
            url = url.resolve(context)
        except AttributeError:
            url = six.text_type(url)
        updates = {}
        for key, value in six.iteritems(self.qs_updates):
            try:
                key = key.resolve(context)
            except AttributeError:
                key = six.text_type(key)
            try:
                value = value.resolve(context)
            except AttributeError:
                value = six.text_type(value)
            updates[key] = value
        new_url = update_query_string(url, updates)
        try:
            do_escape = context.autoescape
        except AttributeError:
            do_escape = True  # By default, escape.
        if do_escape:
            new_url = conditional_escape(new_url)
        return new_url


@register.tag('update_query_string')
def tag_update_query_string(parser, token):
    """Return URL with updated querystring.

    """
    bits = token.split_contents()
    # Quickly check number of arguments.
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'update_query_string' tag "
                                           "requires at least two arguments")
    # Parse options.
    options = {}
    tag_name = bits[0]
    remaining_bits = bits[1:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise template.TemplateSyntaxError(
                'The %r option was specified more than once.' % option)
        if option == 'with':  # "with" is followed by keyword arguments
            value = token_kwargs(remaining_bits, parser)
            if not value:
                raise template.TemplateSyntaxError('"with" in %r tag needs at '
                                                   'least one keyword '
                                                   'argument.' % tag_name)
        else:
            raise template.TemplateSyntaxError(
                'Unknown argument for %r tag: %r.' % (bits[0], option))
        options[option] = value
    qs_updates = options.get('with', {})
    url = None  # For now, we do not support URL as argument.
    return UpdateQueryStringNode(url=url, qs_updates=qs_updates)
