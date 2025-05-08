from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import token_refresh, token_obtain_pair
from django.conf.urls.static import static
from django.conf import settings

from main.views import *

schema_view = get_schema_view(
    openapi.Info(
        title="Book Store API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="vohobjonovsardorbek2005@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += [
    path('token/', token_obtain_pair),
    path('token/refresh/', token_refresh),
]

urlpatterns += [
    path('accounts/register/', RegisterAPIView.as_view(), name='register'),
    path('accounts/me/', UpdateAccountRetrieveUpdateDestroyAPIView.as_view()),
    path('accounts/my-wish-list/', WishListAPIVIew.as_view()),
    path('accounts/<int:pk>/wishlist-add-book/', WishListAddBookAPIView.as_view()),
    path('accounts/<int:pk>/wishlist-remove-book/', WishListRemoveBookAPIView.as_view()),
]

urlpatterns += [
    path('books/', BookListCreateAPIView.as_view()),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyAPIView.as_view()),
    path('books/mine/', MyBookListAPIView.as_view()),
    path('books/<int:pk>/mark-sold/', BookMarkSoldAPIview.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
