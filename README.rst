####################
django-generic-views
####################

django-generic-filters provides generic views to easily add filters to your ListView.

It can handle RawQueryset, Python Object List as well as normal queryset.

It uses a form to define which filters you want and add some options to
your list view.

.. image:: https://secure.travis-ci.org/novapost/django-generic-filters.png?branch=master
   :alt: Build Status
   :target: https://secure.travis-ci.org/novapost/django-generic-filters



*******
Example
*******

**views.py**

.. code-block:: python

    from django_genericfilters.views import FilteredListView


    class UserListView(FilteredListView):
        # Normal ListView options
        template_name = 'user/user_list.html'
        paginate_by = 10
        context_object_name = 'users'

        # FilteredListView options
        form_class = UserListForm
        search_fields = ['first_name', 'last_name', 'username', 'email']
        filter_fields = ['is_active', 'is_staff', 'is_superuser']
        default_order = 'last_name'

        def form_valid(self, form):
            """Return the queryset when form has been submitted."""
            queryset = super(UserListView, self).form_valid(form)

            # Handle specific fields of the custom ListForm
            # Others are automatically handled by FilteredListView

            if form.cleaned_data['is_active'] == 'yes':
                queryset = queryset.filter(is_active=True)
            elif form.cleaned_data['is_active'] == 'no':
                queryset = queryset.filter(is_active=False)

            if form.cleaned_data['is_staff'] == 'yes':
                queryset = queryset.filter(is_staff=True)
            elif form.cleaned_data['is_staff'] == 'no':
                queryset = queryset.filter(is_staff=False)

            if form.cleaned_data['is_superuser'] == 'yes':
                queryset = queryset.filter(is_superuser=True)
            elif form.cleaned_data['is_superuser'] == 'no':
                queryset = queryset.filter(is_superuser=False)

            return queryset


**forms.py**

.. code-block:: python

    from django import forms
    from django.utils.translation import ugettext_lazy as _
    from django_genericfilters import forms as gf


    class UserListForm(gf.QueryFormMixin, gf.OrderFormMixin, gf.FilteredForm):
        is_active = gf.ChoiceField(label=_('Status'),
                                   choices=(('yes', _('Active')),
                                            ('no', _('Unactive'))))

        is_staff = gf.ChoiceField(label=_('Staff'))

        is_superuser = gf.ChoiceField(label=_('Superuser')))

        def get_order_by_choices(self):
            return [('date_joined', _(u'date joined')),
                    ('last_login', _(u'last login')),
                    ('last_name', _(u'Name'))]



*****
Forms
*****

Several form mixin are provided to cover frequent use cases:

* ``OrderFormMixin`` with order_by and order_reverse fields.
* ``QueryFormMixin`` for little full-text search using icontains.

See "mixin" documentation for details.


**********
Ressources
**********

* Documentation: http://django-generic-filters.readthedocs.org
* PyPI page: http://pypi.python.org/pypi/django-generic-filters
* Code repository: https://github.com/novapost/django-generic-filters
* Bugtracker: https://github.com/novapost/django-generic-filters/issues
* Continuous integration: https://travis-ci.org/novapost/django-generic-filters
