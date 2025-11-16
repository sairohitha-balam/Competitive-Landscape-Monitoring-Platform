from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'competitors', views.CompetitorViewSet)
router.register(r'insights', views.InsightViewSet)

urlpatterns = [
    path('', include(router.urls)),
]