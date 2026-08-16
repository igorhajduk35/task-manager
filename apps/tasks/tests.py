from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.tasks.models import Task


class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.userA = User.objects.create_user(
            username="test1",
            password="test1"
        )

        self.userB = User.objects.create_user(
            username="test2",
            password="test2"
        )

        self.taskA = Task.objects.create(
            title="Task A",
            status="TODO",
            priority="LOW",
            created_by=self.userA
        )

        self.taskB = Task.objects.create(
            title="Task B",
            status="TODO",
            priority="LOW",
            created_by=self.userB
        )

        self.taskC = Task.objects.create(
            title="Task C",
            status="TODO",
            priority="LOW",
            created_by=self.userA,
            assigned_to=self.userB
        )


    def test_unauthenticated_get_tasks(self):
        response = self.client.get("/tasks/")

        self.assertEqual(response.status_code, 401)


    def test_authenticated_get_tasks(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/")

        self.assertEqual(response.status_code, 200)


    def test_user_sees_only_accessible_tasks(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/")

        task_ids = [task["id"] for task in response.data["results"]]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIn(self.taskA.id, task_ids)
        self.assertIn(self.taskC.id, task_ids)


    def test_user_sees_assigned_only_to_him_tasks(self):
        self.client.force_authenticate(user=self.userB)
        response = self.client.get("/tasks/")

        task_ids = [task["id"] for task in response.data["results"]]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertNotIn(self.taskA.id, task_ids)
        self.assertIn(self.taskB.id, task_ids)
        self.assertIn(self.taskC.id, task_ids)
        self.assertEqual(response.data["results"][1]["assigned_to"], self.userB.id)
        self.assertEqual(response.data["results"][1]["created_by"], self.userA.id)


    def test_user_cannot_update_task_assigned_to_him(self):
        self.client.force_authenticate(user=self.userB)
        response = self.client.patch(
            f"/tasks/{self.taskC.id}/",
            {
                "title": "Hacked task",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 403)


    def test_user_can_update_own_task(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.patch(
            f"/tasks/{self.taskA.id}/",
            {
                "title": "Updated task",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated task")


    def test_user_cannot_delete_task_assigned_to_him(self):
        self.client.force_authenticate(user=self.userB)
        response = self.client.delete(
            f"/tasks/{self.taskC.id}/"
        )

        self.assertEqual(response.status_code, 403)


    def test_user_can_delete_own_task(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.delete(
            f"/tasks/{self.taskC.id}/"
        )

        self.assertEqual(response.status_code, 204)


    def test_create_task_sets_current_user_as_creator(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.post(
            "/tasks/",
            {
                "created_by": self.userB.id,
                "title": "Correct owner Task",
                "description": "This task was created using tests",
                "due_date": "2027-07-20T15:00:00",
                "status": "COMPLETED",
                "priority": "LOW",
                "assigned_to": None
            },
            format="json"
        )
        
        task = Task.objects.get(id=response.data["id"])


        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["created_by"], self.userA.id)
        self.assertEqual(task.created_by, self.userA)