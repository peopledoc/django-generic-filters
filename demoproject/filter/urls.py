from django.urls import path

from demoproject.filter import views

urlpatterns = [
    path(r"", views.user_list_view, name="user_filter_view"),
]
