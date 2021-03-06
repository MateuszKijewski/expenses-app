from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/balance/', include('balance.urls')),
    path('api/periodic/', include('periodic.urls')),
]
