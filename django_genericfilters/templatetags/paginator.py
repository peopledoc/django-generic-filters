#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/

from django import template

register = template.Library()


def paginator(context, adjacent_pages=1):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    if 'page_obj' in context:
        page_obj = context['page_obj']
        paginator = context['paginator']
        startPage = max(page_obj.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page_obj.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in range(startPage, endPage)
                        if n > 0 and n <= paginator.num_pages]

        context['page_numbers'] = page_numbers
        context['show_first'] = 1 not in page_numbers
        context['show_last'] = paginator.num_pages not in page_numbers
        return context
    else:
        return {}

register.inclusion_tag('snippets/pagination.html',
                       takes_context=True)(paginator)
