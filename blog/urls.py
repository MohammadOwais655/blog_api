from django.contrib import admin
from django.urls import path, include
from main.views.admin_view import admin_site


urlpatterns = [
    path('', include('main.urls')),
    path('admin', admin_site.urls),
]
