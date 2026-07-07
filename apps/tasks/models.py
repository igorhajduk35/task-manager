from django.db import models
from django.contrib.auth.models import User

# Create your models here.

STATUS_CHOICES = {
    # baza przewiduje : frontend wysle
    "TODO": "Todo",
    "IN_PROGRESS": "In progress",
    "COMPLETED": "Completed",
    "ABANDONED": "Abandoned"
}

PRIORITY_CHOICES = {
    "LOW": "Low",
    "HIGH": "High",
    "AVERAGE": "Average"
}

class Task(models.Model):
    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=11,
    )

    priority = models.CharField(
        choices=PRIORITY_CHOICES,
        max_length=7,
    )

    date_created = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_tasks",
    )

    due_date = models.DateTimeField(
        blank=True,
        null=True,
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assigned_tasks",
        blank=True,
        null=True,
    )