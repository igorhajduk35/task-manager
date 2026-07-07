from django.http import JsonResponse
from .models import Task
from django.shortcuts import get_object_or_404
import json
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import TaskSerializer



def task_to_dict(task : Task) -> dict:
    assigned_to = None

    if task.assigned_to is not None:
        assigned_to = task.assigned_to.id

    return(
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "date_created": task.date_created.isoformat(),
            "created_by": task.created_by.id,
            "due_date": task.due_date.isoformat(),
            "assigned_to": assigned_to
        }
    )



# def validate_fields(task : dict) -> bool:
#     if not task["title"] or \
#             not task["status"] or \
#             not task["priority"] or \
#             not task["due_date"]:
#         return False
#     return True



class TasksView(APIView):
    def get(self, request):
        return get_tasks(request)

    def post(self, request):
        return create_task(request)



class TaskDetailView(APIView):
    def get(self, request, id):
        return get_task_by_id(request, id)



# def get_tasks(request):
#     tasks = Task.objects.all()

#     response = []

#     for task in tasks:
#         response.append(task_to_dict(task))

#     return JsonResponse(response, safe=False)



def get_tasks(request):
    tasks = Task.objects.all()

    serializer = TaskSerializer(tasks, many=True)

    return JsonResponse(serializer.data, safe=False)



def get_task_by_id(request, id):
    task = get_object_or_404(Task, id=id)

    return JsonResponse(task_to_dict(task))



# def create_task(request):
#     try:
#         body = request.body
        
#         body_parsed = json.loads(body)

#         created_by_user = User.objects.get(id=1)

#         assigned_to_user = None

#         if body_parsed["assigned_to"] is not None:
#             assigned_to_user = User.objects.get(id=body_parsed["assigned_to"])


#         if not validate_fields(body_parsed):
#             return JsonResponse(
#                 {"error": "Empty form data"},
#                 status=400 # Bad request
#             )
        
#         elif body_parsed["status"].lower() not in ["todo", "in_progress", "completed", "abandoned"] or \
#                 body_parsed["priority"].lower() not in ["low", "high", "average"]:
#             return JsonResponse(
#                 {"error": "Choice not allowed"},
#                 status=400 # Bad request
#             )


#         new_task = Task.objects.create(
#             title=body_parsed["title"],
#             description=body_parsed["description"],
#             status=body_parsed["status"].upper(),
#             priority=body_parsed["priority"].upper(),
#             due_date=datetime.fromisoformat(body_parsed["due_date"]),
#             created_by=created_by_user,
#             assigned_to=assigned_to_user
#         )

#         return JsonResponse(
#             task_to_dict(new_task),
#             status=201 # Created
#         )
    
#     except KeyError:
#         return JsonResponse(
#             {"error": "Field missing"},
#             status=400 # Bad request
#         )
    
#     except ValueError:
#         return JsonResponse(
#             {"error": "Field (probably due_date) wrong type"},
#             status=400 # Bad request
#         )
    
#     except User.DoesNotExist:
#         return JsonResponse(
#             {"error": "User not found"},
#             status=400 # Bad request
#         )
    


def create_task(request):

    serializer = TaskSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            serializer.data,
            status=201 # Created
        )
    
    return Response(
        serializer.errors,
        status=400 # Bad request
    )
