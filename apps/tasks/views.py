from .models import Task
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import TaskSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .permissions import IsTaskCreator
from django.db.models import Q



class TaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = [
        "priority",
        "status",
        "assigned_to",
        "created_by"
    ]
    search_fields = [
        "description",
        "title",
        "assigned_to__username",
        "created_by__username"
    ]
    ordering_fields = [
        "date_created",
        "due_date",
        "priority"
    ]


    def get_queryset(self):
        user = self.request.user

        return Task.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        )


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


    # get_permissions() creates objects, whereas permission_classes stores classes
    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsTaskCreator()]
