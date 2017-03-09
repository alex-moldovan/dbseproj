from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /stocks/
    url(r'^(?P<sectorName>[a-zA-Z0-9_./\s]{1,50})/$', views.sector),
    url(r'^(?P<sectorName>[a-zA-Z0-9_./\s]{1,50})/(?P<symbolName>[a-zA-Z0-9_./\s]{1,50})$', views.stock),
    url(r'^$', views.index, name='index'),
]
