from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions
from django.db.models import Q
from .serializers import UserSerializer
from .models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .serializers import UserSerializer, FriendRequestSerializer, FriendSerializer, PendingFriendRequestSerializer
from .models import User, FriendRequest
from django.core.cache import cache

User = get_user_model()

class SignupView(generics.CreateAPIView):
    """
    This view handles user sign-up by creating a new user instance.
    It uses CreateAPIView to provide the default
    'create' behavior. The queryset includes all User objects, and the
    serializer class used is UserSerializer.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(generics.GenericAPIView):
    """
    This view handles user login. It uses GenericAPIView
    to provide custom behavior for the 'post' method. The serializer class used
    is LoginSerializer. When a POST request is made, it validates the provided
    email and password, authenticates the user, and returns JWT tokens if the
    credentials are valid. If the credentials are invalid, it returns a 401
    Unauthorized response.
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPagination(PageNumberPagination):
    """
    This class defines the pagination behavior for user listings.
    It extends PageNumberPagination and sets
    the page size to 10, meaning each page will contain up to 10 user
    records.
    """
    page_size = 10 

class UserSearchView(generics.ListAPIView):
    """
    This view handles searching for users. It uses ListAPIView to provide 
    the default 'list' behavior. The serializer class used is UserSerializer,
    and it requires the user to be authenticated
    (permission_classes = [permissions.IsAuthenticated]). The pagination
    class used is UserPagination. The get_queryset method filters users
    based on the query parameter 'q', matching either the email exactly
    or the name partially (case-insensitive).
    """
    serializer_class = UserSerializer  
    permission_classes = [permissions.IsAuthenticated]  
    pagination_class = UserPagination  

    def get_queryset(self):
        try:
            query = self.request.query_params.get('q', '')
            return User.objects.filter(
                Q(email__iexact=query) | Q(name__icontains=query)
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to send a friend request.
        """
        from_user = request.user
        to_user_id = request.data.get('to_user_id')
        try:
            to_user = User.objects.get(id=to_user_id)

            # Rate limiting logic
            cache_key = f"friend_request_{from_user.id}"
            request_count = cache.get(cache_key, 0)

            if request_count >= 3:
                return Response({'detail': 'You have exceeded the limit of 3 friend requests per minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Increment the request count and set the cache with a timeout of 60 seconds
            cache.set(cache_key, request_count + 1, timeout=60)

            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
                return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

            friend_request = FriendRequest(from_user=from_user, to_user=to_user)
            friend_request.save()
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': 'Friend request sent.'}, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to accept a friend request.
        """
        try:
            from_user_email = request.data.get('from_user_email')
            from_user = User.objects.get(email=from_user_email)
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=request.user, accepted=False)
            if friend_request.to_user != request.user:
                return Response({'detail': 'Not authorized to accept this friend request.'}, status=status.HTTP_403_FORBIDDEN)
            friend_request.accepted = True
            friend_request.save()
            friend_request.from_user.friends.add(friend_request.to_user)
            friend_request.to_user.friends.add(friend_request.from_user)
            return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectFriendRequestView(generics.DestroyAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to reject a friend request.
        """
        try:
            from_user_email = request.data.get('from_user_email')
            from_user = User.objects.get(email=from_user_email)
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=request.user, accepted=False)
            if friend_request.to_user != request.user:
                return Response({'detail': 'Not authorized to reject this friend request.'}, status=status.HTTP_403_FORBIDDEN)
            friend_request.delete()
            return Response({'detail': 'Friend request rejected.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListFriendsView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        """
        Retrieve the list of friends for the authenticated user.
        """
        return self.request.user.friends.all()
    
class ListPendingFriendRequestsView(generics.ListAPIView):
    serializer_class = PendingFriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        """
        Retrieve the list of pending friend requests for the authenticated user.
        """
        # Filter FriendRequest objects where the to_user is the authenticated user and the request is not yet accepted
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)