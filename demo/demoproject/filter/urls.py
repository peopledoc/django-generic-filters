from django.conf.urls import patterns, url
from demoproject.filter import views


urlpatterns = patterns(
    '',
    url(r'^$', views.user_list_view, name='user_filter_view'),
)
