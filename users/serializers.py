# In users/serializers.py

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

# This correctly gets your active user model (e.g., users.CustomUser)
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Be explicit about the fields you want to show
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Be explicit about the fields required for registration
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use create_user to handle password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user