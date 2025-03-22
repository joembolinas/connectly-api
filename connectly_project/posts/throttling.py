from rest_framework.throttling import UserRateThrottle

class PostCreationRateThrottle(UserRateThrottle):
    """
    Throttle for post creation to prevent spam.
    Limits users to a specific number of post creations per day.
    """
    scope = 'create_post'

class AuthRateThrottle(UserRateThrottle):
    """
    Throttle for authentication attempts to prevent brute force attacks.
    Limits the number of auth attempts per minute.
    """
    scope = 'auth'