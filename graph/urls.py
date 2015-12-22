from django.conf.urls import url

from . import views

app_name = 'graph'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<graph_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<graph_id>[0-9]+)/select/$', views.select, name='select'),
]

