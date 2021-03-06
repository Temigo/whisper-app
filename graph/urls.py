from django.conf.urls import url, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'graphs', views.GraphViewSet)
router.register(r'infections', views.InfectionViewSet)

app_name = 'graph'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^generate/$', views.GenerateGraph.as_view()),
    url(r'^algorithm/$', views.Algorithm.as_view()),
    url(r'^simulate/$', views.SimulateInfection.as_view()),
    url(r'^frontier/$', views.Frontier.as_view()),
    url(r'^import/graph/$', views.ImportGraph.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
