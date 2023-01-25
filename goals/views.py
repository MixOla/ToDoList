from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    permissions
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import (
    Goal,
    GoalCategory, GoalComment, Board
)
from goals.permissions import IsOwnerOrReadOnly, BoardPermissions, GoalCategoryPermissions, GoalPermissions, \
    GoalCommentPermissions
from goals.serializers import (
    GoalCategoryCreateSerializer,
    GoalCategorySerializer,
    GoalCreateSerializer,
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardSerializer, BoardCreateSerializer,
    BoardListSerializer
)


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(
            board__participants__user=self.request.user, is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]

    def get_queryset(self):
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    ''' Класс получения списка целей '''

    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']
    filterset_class = GoalDateFilter

    def get_queryset(self):
        return Goal.objects.filter(
            category__board__participants__user=self.request.user).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self):
        return Goal.objects.filter(category__board__participants__user=self.request.user)

    def perform_destroy(self, instance):
        instance.status = Goal.Status.archived
        instance.save()
        return instance


class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly, GoalCommentPermissions]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class BoardCreateView(CreateAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardListView(ListAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardListSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['title', 'created']

    def get_queryset(self):
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        # Обратите внимание на фильтрацию – она идет через participants
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        # При удалении доски помечаем ее как is_deleted,
        # «удаляем» категории, обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance
