from django.contrib import admin
from django.urls import path
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


# schema_view = get_schema_view(
#     openapi.Info(
#         title="Swagger First Blog ",
#         default_version='v1',
#         description="Test Swagger First Blog",
#         terms_of_service="https://www.ourapp.com/policies/terms/",
#         contact=openapi.Contact(email="contact@swaggerBlog.local"),
#         license=openapi.License(name="Test License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('MyUser.urls')),
    path('buy/', include('buy.urls')),
    path('group/', include('Group.urls')),
    # path('', schema_view.with_ui('swagger', cache_timeout=0),
    #      name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc',
    #      cache_timeout=0), name='schema-redoc'),
]
