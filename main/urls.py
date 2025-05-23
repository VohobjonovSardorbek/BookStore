from django.urls import path
from .views import (
    RegisterAPIView,
    UpdateAccountRetrieveUpdateDestroyAPIView,
    BookListCreateAPIView,
    BookRetrieveUpdateDestroyAPIView,
    MyBookListAPIView,
    BookMarkSoldAPIview,
    WishListAPIVIew,
    WishListAddBookAPIView,
    WishListRemoveBookAPIView,
)

app_name = 'main'  # This is required for namespace

urlpatterns = [
    # Account URLs
    path('account/register/', RegisterAPIView.as_view(), name='account-register'),
    path('account/', UpdateAccountRetrieveUpdateDestroyAPIView.as_view(), name='account-detail'),
    
    # Book URLs
    path('books/', BookListCreateAPIView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyAPIView.as_view(), name='book-detail'),
    path('books/mine/', MyBookListAPIView.as_view(), name='my-books'),
    path('books/<int:pk>/mark-sold/', BookMarkSoldAPIview.as_view(), name='book-mark-sold'),
    
    # Wishlist URLs
    path('wishlist/', WishListAPIVIew.as_view(), name='wishlist-list'),
    path('wishlist/add/<int:pk>/', WishListAddBookAPIView.as_view(), name='wishlist-add-book'),
    path('wishlist/remove/<int:pk>/', WishListRemoveBookAPIView.as_view(), name='wishlist-remove-book'),
]
