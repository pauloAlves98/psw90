from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('', include('usuarios.urls')),
    path('flashcard/', include('flashcard.urls')),
    path('apostilas/', include('apostilas.urls'))
]

if settings.DEBUG:
    urlpatterns+=(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
