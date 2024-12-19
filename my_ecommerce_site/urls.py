from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from products.views import home

urlpatterns = [
    path('admin/', admin.site.urls),                 # Default Django/Jazzmin custom_admin panel
    path('', home, name='home'),                     # Home page
    path('products/', include('products.urls', namespace='products')),
    path('accounts/', include('accounts.urls')),     # Accounts URLs
    path('blog/', include('blog.urls')),             # Blog URLs
    path('tinymce/', include('tinymce.urls')),       # TinyMCE URLs
    path('custom-admin/', include('custom_admin.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
