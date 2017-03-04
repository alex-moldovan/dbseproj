from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /stocks/
    url(r'^$', views.index, name='index'),
]