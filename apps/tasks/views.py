from .models import Task
from django.shortcuts import get_object_or_404
import json
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer



class TasksView(GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True) 

        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        created_by = User.objects.get(id=1)

        if serializer.is_valid():
            serializer.save(created_by=created_by)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED # Created
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class TaskDetailView(GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, pk):
        task = self.get_object()

        serializer = self.get_serializer(task)

        return Response(serializer.data)

