from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Book, Image, WishList

Account = get_user_model()

class AccountTestCase(TestCase):
    def setUp(self):
        self.account = Account.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'test_content',
            content_type='image/jpeg'
        )

    def test_account_creation(self):
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(self.account.username, 'testuser')
        self.assertEqual(self.account.email, 'test@example.com')
        self.assertTrue(self.account.check_password('testpassword123'))

    def test_account_image(self):
        self.account.image = self.test_image
        self.account.save()
        self.assertIsNotNone(self.account.image)

    def test_account_str(self):
        self.assertEqual(str(self.account), 'testuser')

    def test_account_deletion(self):
        self.account.image = self.test_image
        self.account.save()
        image_path = self.account.image.path
        self.account.delete()
        self.assertEqual(Account.objects.count(), 0)

class BookTestCase(TestCase):
    def setUp(self):
        self.account = Account.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.book = Book.objects.create(
            title='Test book',
            details='Test details',
            price=30000.0,
            status='available',
            account=self.account
        )
        self.book2 = Book.objects.create(
            title='Test book2',
            details='Test details 2',
            price=40000.0,
            status='sold',
            account=self.account
        )

    def test_book_creation(self):
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(self.book.title, 'Test book')
        self.assertEqual(self.book.price, 30000.0)
        self.assertEqual(self.book.status, 'available')
        self.assertEqual(self.book.account, self.account)

    def test_book_status_changes(self):
        # Test mark as sold
        self.book.mark_as_sold()
        self.assertEqual(self.book.status, 'sold')

        # Test mark as reserved
        self.book.mark_as_reserved()
        self.assertEqual(self.book.status, 'reserved')

        # Test mark as available
        self.book.mark_as_available()
        self.assertEqual(self.book.status, 'available')

    def test_book_soft_delete(self):
        self.book.soft_delete()
        self.assertTrue(self.book.is_deleted)
        self.assertEqual(Book.objects.count(), 2)  # Still in database
        self.assertEqual(Book.objects.filter(is_deleted=False).count(), 1)

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test book')

class ImageTestCase(TestCase):
    def setUp(self):
        self.account = Account.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.book = Book.objects.create(
            title='Test book',
            price=30000.0,
            status='available',
            account=self.account
        )
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'test_content',
            content_type='image/jpeg'
        )
        self.image = Image.objects.create(
            image=self.test_image,
            is_cover=True,
            book=self.book
        )

    def test_image_creation(self):
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(self.image.book, self.book)
        self.assertTrue(self.image.is_cover)

    def test_image_str(self):
        expected_str = f"Image for {self.book.title}"
        self.assertEqual(str(self.image), expected_str)

    def test_image_deletion(self):
        image_path = self.image.image.path
        self.image.delete()
        self.assertEqual(Image.objects.count(), 0)

class WishListTestCase(TestCase):
    def setUp(self):
        self.account = Account.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.book1 = Book.objects.create(
            title='Test book 1',
            price=30000.0,
            status='available',
            account=self.account
        )
        self.book2 = Book.objects.create(
            title='Test book 2',
            price=40000.0,
            status='available',
            account=self.account
        )
        self.wishlist = WishList.objects.create(account=self.account)

    def test_wishlist_creation(self):
        self.assertEqual(WishList.objects.count(), 1)
        self.assertEqual(self.wishlist.account, self.account)
        self.assertEqual(self.wishlist.books.count(), 0)

    def test_add_book_to_wishlist(self):
        # Test adding a book
        self.assertTrue(self.wishlist.add_book(self.book1))
        self.assertEqual(self.wishlist.books.count(), 1)
        
        # Test adding the same book again
        self.assertFalse(self.wishlist.add_book(self.book1))
        self.assertEqual(self.wishlist.books.count(), 1)

    def test_remove_book_from_wishlist(self):
        # Add a book first
        self.wishlist.add_book(self.book1)
        
        # Test removing the book
        self.assertTrue(self.wishlist.remove_book(self.book1))
        self.assertEqual(self.wishlist.books.count(), 0)
        
        # Test removing a non-existent book
        self.assertFalse(self.wishlist.remove_book(self.book2))
        self.assertEqual(self.wishlist.books.count(), 0)

    def test_wishlist_str(self):
        expected_str = f"{self.account.username}'s Wishlist"
        self.assertEqual(str(self.wishlist), expected_str)

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.account = Account.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.account)
        self.book = Book.objects.create(
            title='Test book',
            details='Test details',
            price=30000.0,
            status='available',
            account=self.account
        )

    def test_book_list(self):
        url = reverse('main:book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_book_create(self):
        url = reverse('main:book-list')
        data = {
            'title': 'New book',
            'details': 'New details',
            'price': 25000.0,
            'status': 'available'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_book_detail(self):
        url = reverse('main:book-detail', kwargs={'pk': self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test book')

    def test_book_update(self):
        url = reverse('main:book-detail', kwargs={'pk': self.book.pk})
        data = {'title': 'Updated book'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated book')

    def test_book_delete(self):
        url = reverse('main:book-detail', kwargs={'pk': self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_deleted)

    def test_book_mark_sold(self):
        url = reverse('main:book-mark-sold', kwargs={'pk': self.book.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 'sold')

class WishListAPITestCase(APITestCase):
    def setUp(self):
        self.account = Account.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.account)
        self.book = Book.objects.create(
            title='Test book',
            price=30000.0,
            status='available',
            account=self.account
        )
        self.wishlist = WishList.objects.create(account=self.account)

    def test_wishlist_list(self):
        url = reverse('main:wishlist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_wishlist_add_book(self):
        url = reverse('main:wishlist-add-book', kwargs={'pk': self.book.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.wishlist.books.count(), 1)

    def test_wishlist_remove_book(self):
        self.wishlist.add_book(self.book)
        url = reverse('main:wishlist-remove-book', kwargs={'pk': self.book.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.wishlist.books.count(), 0)

class AccountAPITestCase(APITestCase):
    def setUp(self):
        self.account_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        self.account = Account.objects.create_user(**self.account_data)
        self.client.force_authenticate(user=self.account)

    def test_account_register(self):
        url = reverse('main:account-register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'  # Added password confirmation
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 2)

    def test_account_detail(self):
        url = reverse('main:account-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_account_update(self):
        url = reverse('main:account-detail')
        data = {'username': 'updateduser'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.username, 'updateduser')


