from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("administration/", include("administration.urls")),
    path("", include("core.urls")),
    path("bus/", include("bus.urls")),
    path("train/", include("train.urls")),
    path("flight/", include("flight.urls")),
    path("support/", include("support.urls")),
]
