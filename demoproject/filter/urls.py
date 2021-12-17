from demoproject.filter import views
from django.conf.urls import url

urlpatterns = [
    url(r"^$", views.user_list_view, name="user_filter_view"),
]
