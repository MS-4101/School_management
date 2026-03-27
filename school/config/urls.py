"""Root URL configuration for School Management Platform."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('library/', include('apps.library_mgmt.urls')),
    path('lab/', include('apps.lab_mgmt.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('buses/', include('apps.buses.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
