from .models import Task
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import TaskSerializer



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=User.objects.get(id=1))
