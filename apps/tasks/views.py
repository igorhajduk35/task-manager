from .models import Task
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import TaskSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
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

    def perform_create(self, serializer):
        serializer.save(created_by=User.objects.get(id=1))
