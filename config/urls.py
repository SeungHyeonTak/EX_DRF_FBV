import debug_toolbar
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.urls')),
    path('api/v1/users/', include('users.urls')),
]

schema_view = get_schema_view(
    openapi.Info(
        title='SNS API',
        default_version='v1',
        description=
        '''
        Django REST Framework Function Base View 공부를 위한 문서
        
        작성자 : SeungHyeon.Tak
        ''',
        terms_of_service='',
        contact=openapi.Contact(name='SeungHyeonTak', email='conficker77@gmail.com'),
        license=openapi.License(name='SNS API TEST')
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=urlpatterns,
)

urlpatterns += [
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
