from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /stocks/
	url(r'^alerts/', views.alerts, name='alerts'),
	url(r'^alert/(?P<alertId>[a-zA-Z0-9_./\s]{1,50})/$', views.alert),
	url(r'^ajax/alerts', views.read_alerts, name='ajax_alerts'),
	url(r'^/$', views.success, name='success'),
	url(r'^ajax/predict', views.predict_future, name='ajax_predict'),
    url(r'^(?P<sectorName>[a-zA-Z0-9_./\s]{1,50})/$', views.sector),
    url(r'^(?P<sectorName>[a-zA-Z0-9_./\s]{1,50})/(?P<symbolName>[a-zA-Z0-9_./\s]{1,50})$', views.stock),
    url(r'^$', views.index, name='index'),
]
