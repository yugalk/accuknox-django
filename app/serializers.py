from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from app.models import UserFriendMapping

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    Defines the fields to be serialized and validated for user signup.
    """

    # Password field for write-only (not displayed in response)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password',
                  'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        """
        Method to create a new user.

        Takes validated data and creates a new CustomUser instance.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    Defines the fields to be serialized for user details.
    """

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class UserFriendMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for UserFriendMapping model.

    Serializes the UserFriendMapping model fields.
    """

    class Meta:
        model = UserFriendMapping
        fields = ('id', 'user', 'friend', 'created_at',)
        read_only_fields = ('id', 'created_at',)
