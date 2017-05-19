from django.conf.urls import url
from demoproject.filter import views


urlpatterns = [
    url(r'^$', views.user_list_view, name='user_filter_view'),
]
