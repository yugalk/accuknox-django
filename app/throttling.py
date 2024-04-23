from rest_framework.throttling import UserRateThrottle


class UserMinRateThrottle(UserRateThrottle):
    """
    Custom throttle class to limit requests based on minimum time between requests for each user.
    """

    def allow_request(self, request, view):
        user = request.user
        if user.is_authenticated:
            self.rate = '3/minute'  # Rate limit
            self.num_requests, self.duration = self.parse_rate(self.rate)  # Add this

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
