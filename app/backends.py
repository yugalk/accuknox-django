from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CaseInsensitiveModelBackend(ModelBackend):
    """
    Custom authentication backend for case-insensitive email login.

    Authenticate users by email address in a case-insensitive manner.
    Lookup is done by email, and authentication succeeds if the password matches.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Case-insensitive email lookup
            user = User.objects.get(email__iexact=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
