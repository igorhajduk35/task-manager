from rest_framework import serializers
from .models import Task


# Meta seperates class' behaviour from its configuration, Meta being the configuration


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"