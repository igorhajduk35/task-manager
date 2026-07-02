from django.shortcuts import render
from django.http import HttpResponse
from .models import Task
import json

def TaskView(request):
    all_tasks = Task.objects.all()

    json_response = []

    for task in all_tasks:
        print("task")

        json_response.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "date_created": str(task.date_created),
                "created_by": task.created_by.id,
                "due_date": str(task.due_date),
                # set to null if NoneType else set to task.assigned_to.id
                "assigned_to": "" 
            }
        )

    return HttpResponse(json.dumps(json_response))