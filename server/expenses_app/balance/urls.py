from django.urls import path, include

from rest_framework.routers import DefaultRouter

from balance import views

router = DefaultRouter()
router.register('incomes', views.IncomeViewSet)

app_name = 'balance'

urlpatterns = [
    path('', include(router.urls))
]