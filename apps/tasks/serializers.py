from rest_framework import serializers
from .models import Task


# Meta seperates class' behaviour from its configuration, Meta being the configuration


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        # read_only_fields will be ignored while adding to database
        read_only_fields = (
            "id",
            "date_created",
            "created_by",
        )