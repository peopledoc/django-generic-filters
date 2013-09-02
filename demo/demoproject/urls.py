from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


home = TemplateView.as_view(template_name='home.html')


urlpatterns = patterns(
    '',
    url(r'^filter/', include('demoproject.filter.urls')),
    # An informative homepage.
    url(r'', home, name='home')
)
