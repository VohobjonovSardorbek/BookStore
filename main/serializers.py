from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Account, Book, Image, WishList

Account = get_user_model()

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'image', 'date_joined']
        read_only_fields = ['date_joined']

class AccountPostSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'image']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = Account.objects.create_user(**validated_data)
        return user

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'is_cover', 'book', 'created_at']
        read_only_fields = ['created_at']

class BookSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'details', 'price', 'status', 'account', 'images', 
                 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class BookPostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = ['title', 'details', 'price', 'status', 'images']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        if value > 1000000:
            raise serializers.ValidationError("Price cannot exceed 1,000,000")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        book = Book.objects.create(**validated_data)
        
        for image_data in images_data:
            Image.objects.create(book=book, **image_data)
        
        return book

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        
        # Update book fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update images if provided
        if images_data:
            instance.images.all().delete()  # Remove existing images
            for image_data in images_data:
                Image.objects.create(book=instance, **image_data)
        
        return instance

class BookMarkSoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'sold')
        extra_kwargs = {
            'sold': {
                'read_only': True
            }
        }

class WishListSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    account = AccountSerializer(read_only=True)

    class Meta:
        model = WishList
        fields = ['id', 'account', 'books', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
