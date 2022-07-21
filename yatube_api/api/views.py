from django.shortcuts import get_object_or_404
from rest_framework import pagination, permissions, viewsets, mixins
from rest_framework.filters import SearchFilter

from posts.models import Follow, Group, Post, User
from .permissions import OwnerOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer, UserSerializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (OwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_post(self):
        return get_object_or_404(
            Post, pk=self.kwargs.get('post_id')
        )

    def get_queryset(self):
        return self.get_post().comments


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (SearchFilter,)
    search_fields = ('following__username', 'user__username',)

    def get_queryset(self):
        """Возвращает все подписки пользователя, сделавшего запрос"""
        new_queryset = Follow.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
