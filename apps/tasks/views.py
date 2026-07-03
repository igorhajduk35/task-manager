from django.http import JsonResponse
from .models import Task
from django.shortcuts import get_object_or_404



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




def TaskView(request):
    all_tasks = Task.objects.all()

    json_response = []

    for task in all_tasks:
        json_response.append(TaskToJson(task))

    return JsonResponse(json_response, safe=False)




def GetTaskById(request, id):
    task = get_object_or_404(Task, id=id)

    return JsonResponse(TaskToJson(task))