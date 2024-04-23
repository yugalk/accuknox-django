from django.urls import path
from app.views import (LoginAPI, SignUpAPI, UserSearchAPI, SendFriendRequestAPI, FriendRequestAPI, FriendsAPI,
                        LogoutAPI)

urlpatterns = [
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('signup/', SignUpAPI.as_view(), name='signup'),
    path('search/', UserSearchAPI.as_view(), name='user_search'),
    path('user/friends/', FriendsAPI.as_view(), name='friends'),
    path('user/friends/request/send', SendFriendRequestAPI.as_view(), name='send_friend_requests'),
    path('user/friends/request', FriendRequestAPI.as_view(), name='friend_requests')
]
