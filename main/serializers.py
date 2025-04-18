from rest_framework import serializers
from .models import Account, Book, Image


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'image', 'date_joined')
        extra_kwargs = {
            'password' : {
                'write_only' : True
            }
        }

    def create(self, validate_data):
        return Account.objects.create_user(**validate_data)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image')


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        images = ImageSerializer(many=True, read_only=True)
        model = Book
        fields = '__all__'


class BookPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        extra_kwargs = {
            'account' : {
                "read_only" : True
            }
        }


class BookMarkSoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'sold')
        extra_kwargs = {
            'sold':{
                'read_only' : True
            }
        }