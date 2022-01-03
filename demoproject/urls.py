from django.urls import include, path
from django.views.generic import TemplateView

home = TemplateView.as_view(template_name="home.html")


urlpatterns = [
    path(r"filter/", include("demoproject.filter.urls")),
    # An informative homepage.
    path(r"", home, name="home"),
]
