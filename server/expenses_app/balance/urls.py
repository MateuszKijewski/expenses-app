from django.urls import path, include

from rest_framework.routers import DefaultRouter

from balance import views

router = DefaultRouter()
router.register('operations', views.OperationViewSet)
router.register('limited', views.LimitedCategoryViewSet)

app_name = 'balance'

urlpatterns = [
    path('', include(router.urls)),
    path('operations/delete', views.OperationDelete.as_view(), name='delete')
]