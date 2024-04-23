from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.models import User, UserFriendMapping, ExpiryToken
from app.serializers import SignUpSerializer, UserSerializer, UserFriendMappingSerializer
from app.throttling import UserMinRateThrottle
from app.authentication import ExpiringTokenAuthentication


class SignUpAPI(generics.CreateAPIView):
    """
    API endpoint to register a new user.

    Accepts email, password, first_name, and last_name in the request body.
    Returns the newly created user details or validation errors.
    """
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        # Deserialize request data
        serializer = SignUpSerializer(data=request.data)

        # Validate and save user to db
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    """
    API endpoint to authenticate and login a user.

    Accepts email and password in the request body.
    Returns a refresh token and an access token upon successful login.
    """

    def post(self, request, *args, **kwargs):
        # Get email and password from request data
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        # Check authentication and Generate tokens
        if user:
            token, created = ExpiryToken.objects.get_or_create(user=user)

            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                },
                'token': token.key,
            }, status=status.HTTP_200_OK)
        else:
            # Return error for invalid credentials
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserSearchAPI(APIView, PageNumberPagination):
    """
    API endpoint to search users by email or name.

    Accepts a search keyword in the query parameter.
    Paginates results with up to 10 records per page.
    """

    authentication_classes = [ExpiringTokenAuthentication]  # Token authentication required
    permission_classes = [IsAuthenticated]  # User must be authenticated
    page_size = 10

    def get(self, request, *args, **kwargs):
        # Get search keyword from query parameters
        search_keyword = request.query_params.get('q', '').strip()
        self.page_size = request.query_params.get('page_size', self.page_size)

        if not search_keyword:
            return Response({'error': 'Search query cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter users by email if search keyword is an exact match
        if '@' in search_keyword and '.' in search_keyword:
            try:
                user = User.objects.get(email=search_keyword.lower())
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Filter users by name if search keyword is a substring of the name
        elif search_keyword:
            queryset = User.objects.filter(
                Q(first_name__icontains=search_keyword) |
                Q(last_name__icontains=search_keyword)
            )

        # Paginate queryset
        paginated_queryset = self.paginate_queryset(queryset, request)

        # Serialize and return paginated queryset
        serializer = UserSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


class SendFriendRequestAPI(APIView):
    """
    API endpoint to send a friend request.

    Allows users to send a friend request to another user.
    """
    authentication_classes = [ExpiringTokenAuthentication]  # Token authentication required
    permission_classes = [IsAuthenticated]  # User must be authenticated
    throttle_classes = [UserMinRateThrottle]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')

        # Validate if to_user_id exists
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent sending friend request to oneself
        if request.user.id == to_user_id:
            return Response({'error': 'You cannot send friend request to yourself.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a friend already exists
        if UserFriendMapping.objects.filter(friend=request.user, user=to_user_id).exists():
            return Response({'error': 'You are friends already.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a friend request already exists
        if UserFriendMapping.objects.filter(user=request.user, friend_id=to_user_id).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = UserFriendMapping(user=request.user, friend_id=to_user_id)
        friend_request.save()

        serializer = UserFriendMappingSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FriendRequestAPI(APIView, PageNumberPagination):
    authentication_classes = [ExpiringTokenAuthentication]  # Token authentication required
    permission_classes = [IsAuthenticated]  # User must be authenticated
    page_size = 10

    def get(self, request, *args, **kwargs):
        """
        API endpoint to list friend requests (received friend requests).

        - Retrieves friend mappings with 'pending' request_status for the user.
        - Returns paginated list of friend requests.

        Returns:
        - Response: Paginated list of friends requests.
        """
        # Get friend mappings where request is accepted
        friend_mappings = UserFriendMapping.objects.filter(friend=request.user, request_status='pending')

        # Pagination
        paginated_friend_requests = self.paginate_queryset(friend_mappings, request)

        # Serialize friends
        serializer = UserFriendMappingSerializer(paginated_friend_requests, many=True)
        return self.get_paginated_response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        API endpoint to accept or reject a friend request.

        - Accepts request_id and action ('accept' or 'reject') in the request body.
        - Updates the request_status field in UserFriendMapping to 'accepted' or 'rejected'.

        Parameters:
        - request_id (int): ID of the friend request to accept or reject.
        - action (str): Action to perform ('accept' or 'reject').

        Returns:
        - Response: JSON response with the updated friend request details or an error message.
        """
        request_id = request.data.get('request_id')
        action = request.data.get('action')

        if not request_id or not action:
            return Response({'error': 'request_id and action are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = UserFriendMapping.objects.get(id=request_id)
        except UserFriendMapping.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the friend request is for the current user
        if friend_request.friend != request.user:
            return Response({'error': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        if friend_request.request_status != 'pending':
            return Response({'error': 'Friend request is not pending.'}, status=status.HTTP_200_OK)
        if action == 'accept':
            friend_request.request_status = 'accepted'
            friend_request.save()
            return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            friend_request.request_status = 'rejected'
            friend_request.save()
            return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


class FriendsAPI(APIView, PageNumberPagination):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]
    page_size = 10

    def get(self, request, *args, **kwargs):
        """
        API endpoint to list friends (users who have accepted friend requests).

        - Retrieves friend mappings with 'accepted' request_status for the current user.
        - Returns paginated list of friends.

        Returns:
        - Response: Paginated list of friends.
        """
        # Get friend mappings where request is accepted
        friend_mappings = UserFriendMapping.objects.filter(
            Q(friend=request.user) | Q(user=request.user),
            request_status='accepted'
        )

        # Get list of friends
        # Extracting users and friends from friend_mappings in a single list comprehension
        friends = [mapping.user if mapping.friend == request.user else mapping.friend for mapping in
                   friend_mappings]

        # Removing duplicates by converting the list to a set and back to a list
        friends = list(set(friends))
        # Pagination
        paginated_friends = self.paginate_queryset(friends, request)

        # Serialize friends
        serializer = UserSerializer(paginated_friends, many=True)
        return self.get_paginated_response(serializer.data)


class LogoutAPI(APIView):
    """
    API Endpoint to log out the user
    Invalidates user's token to log out the user.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def post(self, request, *args, **kwargs):
        # Get the user's token
        user_token = request.user.auth_token

        if user_token:
            # Delete the token
            user_token.delete()

        # Logout successfully
        return Response({"detail": "Successfully logged out"}, status=200)
