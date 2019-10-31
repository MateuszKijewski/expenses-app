from django.conf.urls import url
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from balance import views

router = DefaultRouter()
router.register('operations', views.OperationViewSet)
router.register('limited', views.LimitedCategoryViewSet)
router.register('savings', views.SavingViewSet)

app_name = 'balance'

urlpatterns = [
    path('operations/delete', views.OperationDelete.as_view(), name='delete'),
    url(r'savings/(?P<saving_id>.+)/operations', views.SavingOperations.as_view(), name='saving_operations'),
    path('', include(router.urls))
]