from django.urls import path, include

from rest_framework.routers import DefaultRouter

from periodic import views

router = DefaultRouter()
router.register('reccuring', views.ReccurentPaymentViewSet, base_name='reccurent')

app_name = 'periodic'

urlpatterns = [
    path('', include(router.urls)),
]