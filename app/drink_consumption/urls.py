from django.urls import include, path
from rest_framework import routers
from . import api
from . import views


router = routers.DefaultRouter()
router.register(r'containers', api.ContainerViewSet)
router.register(r'products', api.ProductViewSet)

urlpatterns = [
    path('api/scan/', api.tag_scan),
    path('api/history/', api.get_reffil_list),
    path('api/', include(router.urls)),
    path('register/', views.register),
    path('u/dashboard', views.personnal_dashboard),
    path('u/', include('django.contrib.auth.urls')),
    path('', views.dashboard),
]
