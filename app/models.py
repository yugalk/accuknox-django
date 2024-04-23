from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

from app.constants import REQUEST_STATUS_CHOICES


class CustomUserManager(BaseUserManager):
    """
        Custom user manager for the custome User model.
        
        Provides method to create user instance.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
            Create a new user instance.
            
            Creates and returns a new User instance with the given email and password.
        """
        if not email:
            raise ValueError("Email field must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
        Custom user model for the application.
        
        Inherits from AbstractBaseUser to customize user fields.
    """
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserFriendMapping(models.Model):
    """
    Model to represent user friendships.

    Represents a mapping between two users who are friends.
    """
    user = models.ForeignKey(
        User,
        related_name='user_friend_mappings',
        on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    request_status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend',)


class ExpiryToken(Token):
    # Set the expiry time to 1 hour
    expires = models.DateTimeField(default=timezone.now() + timezone.timedelta(hours=1))

    def has_expired(self):
        # Check if token has expired
        return timezone.now() >= self.expires
