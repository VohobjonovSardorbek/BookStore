from django.dispatch import receiver
from django.db.models.signals import post_delete
import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Account(AbstractUser):
    image = models.ImageField(
        upload_to='accounts/',
        null=True,
        blank=True,
        help_text=_('Profile picture of the user')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        # Delete user's image when account is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('sold', _('Sold')),
        ('reserved', _('Reserved'))
    ]

    title = models.CharField(
        max_length=255,
        db_index=True,
        help_text=_('Title of the book')
    )
    details = models.TextField(
        blank=True,
        null=True,
        help_text=_('Detailed description of the book')
    )
    price = models.FloatField(
        validators=[
            MinValueValidator(0.0, message=_('Price cannot be negative')),
            MaxValueValidator(1000000.0, message=_('Price cannot exceed 1,000,000'))
        ],
        help_text=_('Price of the book')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True,
        help_text=_('Current status of the book')
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='books',
        help_text=_('Owner of the book')
    )

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'status']),
            models.Index(fields=['price', 'status']),
        ]

    def __str__(self):
        return self.title

    def soft_delete(self):
        """Soft delete the book instead of permanent deletion"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def mark_as_sold(self):
        """Mark the book as sold"""
        self.status = 'sold'
        self.save(update_fields=['status'])

    def mark_as_reserved(self):
        """Mark the book as reserved"""
        self.status = 'reserved'
        self.save(update_fields=['status'])

    def mark_as_available(self):
        """Mark the book as available"""
        self.status = 'available'
        self.save(update_fields=['status'])


class Image(models.Model):
    image = models.ImageField(
        upload_to='books/',
        blank=True,
        null=True,
        help_text=_('Image of the book')
    )
    is_cover = models.BooleanField(
        default=False,
        help_text=_('Whether this is the cover image')
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='images',
        help_text=_('Book this image belongs to')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        ordering = ['-created_at']

    def __str__(self):
        return f"Image for {self.book.title}"

    def delete(self, *args, **kwargs):
        # Delete the image file when the model instance is deleted
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)


class WishList(models.Model):
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='wishlist',
        help_text=_('Account this wishlist belongs to')
    )
    books = models.ManyToManyField(
        Book,
        related_name='wishlists',
        help_text=_('Books in the wishlist')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.account.username}'s Wishlist"

    def add_book(self, book):
        """Add a book to the wishlist if it's not already there"""
        if not self.books.filter(id=book.id).exists():
            self.books.add(book)
            return True
        return False

    def remove_book(self, book):
        """Remove a book from the wishlist if it exists"""
        if self.books.filter(id=book.id).exists():
            self.books.remove(book)
            return True
        return False




