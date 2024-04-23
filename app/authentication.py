from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from app.models import ExpiryToken


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Expiring Token Authentication.

    Custom authentication class that extends TokenAuthentication to add token expiry.
    """
    model = ExpiryToken

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if token.has_expired():
            raise AuthenticationFailed("Token has expired")

        return (token.user, token)
