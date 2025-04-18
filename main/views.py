from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.status import *

from .models import WishList
from .serializers import *
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny
from django_filters.rest_framework import DjangoFilterBackend


class BookPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 500000


class RegisterAPIView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save()
        WishList.objects.create(account=serializer.instance)


class UpdateAccountRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = AccountSerializer

    def get_object(self):
        return self.request.user


class BookListCreateAPIView(ListCreateAPIView):
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['cover', 'account', 'sold']
    search_fields = ['title']
    ordering_fields = ['price', 'created_at']
    pagination_class = BookPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='sold',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description='Filter books by sales.',
            ),
            openapi.Parameter(
                name='account',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Filter books by account.'
            ),
            openapi.Parameter(
                name='cover',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter books by cover.'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BookSerializer
        return BookPostSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)


class BookRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BookSerializer
        return BookPostSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        if serializer.instance.account != self.request.user:
            raise PermissionDenied("Siz ushbu kitobni tahrirlash huquqiga ega emassiz!")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.account != self.request.user:
            raise PermissionDenied("Siz ushbu kitobni o'chirish huquqiga ega emassiz!")
        instance.delete()


class MyBookListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sold', 'cover']
    search_fields = ['title']
    ordering_fields = ['title', 'price', 'created_at']
    pagination_class = BookPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='sold',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description='Filter books by sales.',
            ),
            openapi.Parameter(
                name='cover',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter books by cover.'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Book.objects.filter(account=self.request.user)



class BookMarkSoldAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        book = get_object_or_404(Book, id=pk, account=request.user)
        serializer = BookMarkSoldSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save(sold=True)
            response = {
                "success" : True,
                'message' : 'Book marked sold.',
                'data' : BookSerializer(book).data
            }
            return Response(response, status=HTTP_200_OK)
        response = {
            "success" : False,
            'errors' : serializer.errors
        }
        return Response(response, status=HTTP_400_BAD_REQUEST)


class WishListAPIVIew(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

    def get_queryset(self):
        wishlist = WishList.objects.get(account=self.request.user)
        return wishlist.books.order_by('title')


class WishListAddBookAPIView(APIView):
    def post(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        wishlist = WishList.objects.get(account=request.user)
        wishlist.books.add(book)
        wishlist.save()
        response = {
            "success" : True,
            'message' : 'Book added to wishlist!',
        }
        return Response(response, status=HTTP_201_CREATED)


class WishListRemoveBookAPIView(APIView):
    def delete(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        wishlist = WishList.objects.get(account=request.user)
        wishlist.books.remove(book)
        wishlist.save()
        response = {
            "success" : True,
            'message' : "Book removed from wishlist."
        }
        return Response(response, status=HTTP_204_NO_CONTENT)