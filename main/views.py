from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.status import *
from django.shortcuts import get_object_or_404

from .serializers import *
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny
from django_filters.rest_framework import DjangoFilterBackend


class BookPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class RegisterAPIView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountPostSerializer

    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=AccountPostSerializer,
        responses={
            201: AccountSerializer,
            400: "Bad Request - Invalid data"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        account = serializer.save()
        WishList.objects.create(account=account)


class UpdateAccountRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    @swagger_auto_schema(
        operation_description="Get current user's account details",
        responses={
            200: AccountSerializer,
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update current user's account details",
        request_body=AccountSerializer,
        responses={
            200: AccountSerializer,
            400: "Bad Request - Invalid data",
            401: "Unauthorized"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class BookListCreateAPIView(ListCreateAPIView):
    queryset = Book.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'account']
    search_fields = ['title', 'details']
    ordering_fields = ['price', 'created_at']
    pagination_class = BookPagination

    @swagger_auto_schema(
        operation_description="List all books with filtering and search capabilities",
        manual_parameters=[
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter books by status (available, sold, reserved)',
                enum=['available', 'sold', 'reserved']
            ),
            openapi.Parameter(
                name='account',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Filter books by account ID'
            ),
            openapi.Parameter(
                name='search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Search in title and details'
            ),
            openapi.Parameter(
                name='ordering',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Order by field (e.g., price, created_at)'
            )
        ],
        responses={
            200: BookSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new book",
        request_body=BookPostSerializer,
        responses={
            201: BookSerializer,
            400: "Bad Request - Invalid data",
            401: "Unauthorized"
        }
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

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
    queryset = Book.objects.filter(is_deleted=False)
    serializer_class = BookSerializer

    @swagger_auto_schema(
        operation_description="Get book details by ID",
        responses={
            200: BookSerializer,
            404: "Book not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update book details",
        request_body=BookPostSerializer,
        responses={
            200: BookSerializer,
            400: "Bad Request - Invalid data",
            401: "Unauthorized",
            403: "Permission denied",
            404: "Book not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a book (soft delete)",
        responses={
            204: "No content",
            401: "Unauthorized",
            403: "Permission denied",
            404: "Book not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

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
            raise PermissionDenied("You don't have permission to edit this book!")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.account != self.request.user:
            raise PermissionDenied("You don't have permission to delete this book!")
        instance.soft_delete()


class MyBookListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'details']
    ordering_fields = ['title', 'price', 'created_at']
    pagination_class = BookPagination

    @swagger_auto_schema(
        operation_description="List current user's books",
        manual_parameters=[
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter books by status (available, sold, reserved)',
                enum=['available', 'sold', 'reserved']
            )
        ],
        responses={
            200: BookSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Book.objects.filter(account=self.request.user, is_deleted=False)


class BookMarkSoldAPIview(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mark a book as sold",
        responses={
            200: BookSerializer,
            401: "Unauthorized",
            403: "Permission denied",
            404: "Book not found"
        }
    )
    def patch(self, request, pk):
        book = get_object_or_404(Book, id=pk, account=request.user, is_deleted=False)
        book.mark_as_sold()
        response = {
            "success": True,
            'message': 'Book marked as sold.',
            'data': BookSerializer(book).data
        }
        return Response(response, status=HTTP_200_OK)


class WishListAPIVIew(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    pagination_class = BookPagination

    @swagger_auto_schema(
        operation_description="Get current user's wishlist",
        responses={
            200: BookSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        wishlist = get_object_or_404(WishList, account=self.request.user)
        return wishlist.books.filter(is_deleted=False).order_by('title')


class WishListAddBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add a book to wishlist",
        responses={
            201: "Book added to wishlist",
            400: "Book already in wishlist",
            401: "Unauthorized",
            404: "Book not found"
        }
    )
    def post(self, request, pk):
        book = get_object_or_404(Book, id=pk, is_deleted=False)
        wishlist = get_object_or_404(WishList, account=request.user)

        if wishlist.add_book(book):
            response = {
                "success": True,
                'message': 'Book added to wishlist!',
            }
            return Response(response, status=HTTP_201_CREATED)

        response = {
            "success": False,
            'message': 'Book is already in wishlist.',
        }
        return Response(response, status=HTTP_400_BAD_REQUEST)


class WishListRemoveBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Remove a book from wishlist",
        responses={
            204: "Book removed from wishlist",
            400: "Book not in wishlist",
            401: "Unauthorized",
            404: "Book not found"
        }
    )
    def delete(self, request, pk):
        book = get_object_or_404(Book, id=pk, is_deleted=False)
        wishlist = get_object_or_404(WishList, account=request.user)

        if wishlist.remove_book(book):
            response = {
                "success": True,
                'message': "Book removed from wishlist."
            }
            return Response(response, status=HTTP_204_NO_CONTENT)

        response = {
            "success": False,
            'message': "Book is not in wishlist."
        }
        return Response(response, status=HTTP_400_BAD_REQUEST)

