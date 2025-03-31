from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from userauths.models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that adds user information to the token"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['full_name'] = user.full_name
        token['email'] = user.email
        
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation"""
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2']
        
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user with encrypted password"""
        # Remove password2 as it's not needed for creating the user
        validated_data.pop('password2', None)
        
        user = User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
        )
        
        # Extract username from email
        email_username = user.email.split("@")[0]
        user.username = email_username
        
        # Set encrypted password
        user.set_password(validated_data['password'])
        user.save()
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model"""
    
    class Meta:
        model = Profile
        fields = '__all__'