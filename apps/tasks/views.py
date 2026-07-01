from django.shortcuts import render
from django.http import HttpResponse

def TaskView(request):
    return HttpResponse("Hello tasks!")