from django.http import JsonResponse
from .models import Task
from django.shortcuts import get_object_or_404
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User



def TaskToJson(task):
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



def TaskFieldsEmpty(task):
    ...


@csrf_exempt
def TaskView(request):
    if request.method == "GET": return GetTasks(request)

    elif request.method == "POST": return CreateTask(request)

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405 # Method not allowed
    )



def GetTasks(request):
    all_tasks = Task.objects.all()

    json_response = []

    for task in all_tasks:
        json_response.append(TaskToJson(task))

    return JsonResponse(json_response, safe=False)



def GetTaskById(request, id):
    task = get_object_or_404(Task, id=id)

    return JsonResponse(TaskToJson(task))



def CreateTask(request):
    try:
        body = request.body
        
        body_parsed = json.loads(body)

        created_by_user = User.objects.get(id=1)

        assigned_to_user = None

        if body_parsed["assigned_to"] is not None:
            assigned_to_user = User.objects.get(id=body_parsed["assigned_to"])


        if not body_parsed["title"] or \
                not body_parsed["status"] or \
                not body_parsed["priority"] or \
                not body_parsed["due_date"]:
            return JsonResponse(
                {"error": "Empty form data"},
                status=400 # Bad request
            )
        
        elif body_parsed["status"].lower() not in ["todo", "in_progress", "completed", "abandoned"] or \
                body_parsed["priority"].lower() not in ["low", "high", "average"]:
            return JsonResponse(
                {"error": "Choice not allowed"},
                status=400 # Bad request
            )


        new_task = Task.objects.create(
            title=body_parsed["title"],
            description=body_parsed["description"],
            status=body_parsed["status"].upper(),
            priority=body_parsed["priority"].upper(),
            due_date=datetime.fromisoformat(body_parsed["due_date"]),
            created_by=created_by_user,
            assigned_to=assigned_to_user
        )

        return JsonResponse(
            TaskToJson(new_task),
            status=201 # Created
        )
    
    except KeyError:
        return JsonResponse(
            {"error": "Field missing"},
            status=400 # Bad request
        )
    
    except ValueError:
        return JsonResponse(
            {"error": "Field (probably due_date) wrong type"},
            status=400 # Bad request
        )
    
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"},
            status=400 # Bad request
        )