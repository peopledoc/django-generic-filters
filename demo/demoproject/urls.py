from django.conf.urls import include, url
from django.views.generic import TemplateView


home = TemplateView.as_view(template_name='home.html')


urlpatterns = [
    url(r'^filter/', include('demoproject.filter.urls')),
    # An informative homepage.
    url(r'', home, name='home')
]
