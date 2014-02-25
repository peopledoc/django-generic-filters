# -*- coding: utf-8 -*-

from django_genericfilters.views import FilteredListView

from django.contrib.auth.models import User

from demoproject.filter.forms import UserListForm


class UserListView(FilteredListView):
    # Normal ListView options
    template_name = 'user/user_list.html'
    paginate_by = 10
    context_object_name = 'users'
    model = User

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


user_list_view = UserListView.as_view()
