from rest_framework import serializers
from .models import Task
from django.utils import timezone


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

    def validate(self, attrs):
        due_date = attrs.get("due_date")

        if due_date is not None and due_date < timezone.now():
            raise serializers.ValidationError({
                "due_date": "Due date cannot be set in the past."
            })

        return attrs