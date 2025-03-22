class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.settings = {}

# Add new utility functions below

def get_paginated_response(paginator, queryset, serializer_class, request):
    """
    Create a paginated response from a queryset using the specified serializer.
    
    Args:
        paginator: The paginator instance to use
        queryset: The queryset to paginate
        serializer_class: The serializer class to use for objects
        request: The current request object
        
    Returns:
        A paginated Response object
    """
    from rest_framework.response import Response
    
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = serializer_class(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)

def handle_exception(exc):
    """
    Standardized exception handler for API views.
    
    Args:
        exc: The exception that was raised
        
    Returns:
        A Response object with appropriate error details and status code
    """
    from rest_framework.response import Response
    from rest_framework import status
    from django.db import IntegrityError
    from django.core.exceptions import ValidationError
    
    if isinstance(exc, ValidationError):
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, IntegrityError):
        return Response({'detail': 'Database integrity error occurred'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Default handler for unexpected exceptions
    return Response(
        {'detail': 'An unexpected error occurred'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

def validate_post_ownership(post, user):
    """
    Validate that a user owns a post.
    
    Args:
        post: The post object to check
        user: The user to verify against
        
    Raises:
        PermissionError: If the user does not own the post
    """
    if post.author != user:
        raise PermissionError("You don't have permission to modify this post")