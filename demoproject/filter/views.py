from django.contrib.auth.models import User

from demoproject.filter.forms import UserListForm
from django_genericfilters.views import FilteredListView


class UserListView(FilteredListView):
    # Normal ListView options
    template_name = "user/user_list.html"
    paginate_by = 10
    context_object_name = "users"
    model = User

    # FilteredListView options
    form_class = UserListForm
    search_fields = ["first_name", "last_name", "username", "email"]
    filter_fields = ["is_active", "is_staff", "is_superuser"]
    default_order = "last_name"


user_list_view = UserListView.as_view()
