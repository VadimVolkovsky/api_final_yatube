from django.urls import include, path
from rest_framework import routers

from .views import PostViewSet, CommentViewSet, UserViewSet, GroupViewSet, FollowViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'posts', PostViewSet)
router_v1.register(r'users', UserViewSet)
router_v1.register(r'groups', GroupViewSet)
router_v1.register(r'follow', FollowViewSet)
router_v1.register(r'posts/(?P<post_id>\d+)/comments',
                   CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router_v1.urls))
]
