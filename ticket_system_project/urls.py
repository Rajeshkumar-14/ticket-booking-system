from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("apps.authentication.urls", namespace="auth")),
    path("administration/", include("apps.administration.urls", namespace="administration")),
    path("", include("apps.core.urls", namespace="core")),
    path("bus/", include("apps.bus.urls", namespace="bus")),
    path("train/", include("apps.train.urls", namespace="train")),
    path("flight/", include("apps.flight.urls", namespace="flight")),
    path("support/", include("apps.support.urls", namespace="support")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
