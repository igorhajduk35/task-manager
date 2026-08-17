from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from apps.tasks.models import Task
# from django.db.models import Case, When, IntegerField


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
            status="ABANDONED",
            priority="LOW",
            created_by=self.userB
        )

        self.taskC = Task.objects.create(
            title="Task C",
            status="COMPLETED",
            priority="HIGH",
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


    def test_cannot_create_task_with_past_due_date(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.post(
            "/tasks/",
            {
                "title": "Past Task",
                "description": "This should not work",
                "due_date": "2025-07-20T15:00:00",
                "status": "COMPLETED",
                "priority": "LOW",
                "assigned_to": None
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)


    def test_can_create_task_with_future_due_date(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.post(
            "/tasks/",
            {
                "title": "Future Task",
                "description": "This should work",
                "due_date": "2050-07-20T15:00:00",
                "status": "COMPLETED",
                "priority": "LOW",
                "assigned_to": None
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)


    def test_cannot_update_due_date_to_past(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.patch(
            f"/tasks/{self.taskA.id}/",
            {
                "due_date": "2020-07-20T15:00:00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)


    def test_can_update_due_date_to_future(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.patch(
            f"/tasks/{self.taskA.id}/",
            {
                "due_date": "2040-07-20T15:00:00"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)


    def test_cannot_create_task_with_invalid_status(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.post(
            "/tasks/",
            {
                "title": "Future Task",
                "description": "This should work",
                "due_date": "2050-07-20T15:00:00",
                "status": "idk",
                "priority": "LOW",
                "assigned_to": None
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)


    def test_cannot_create_task_without_title(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.post(
            "/tasks/",
            {
                "description": "Task without title",
                "due_date": "2050-07-20T15:00:00",
                "status": "TODO",
                "priority": "LOW",
                "assigned_to": None
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)


    def test_filter_tasks_by_status(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/?status=TODO")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "TODO")

    
    def test_search_tasks_by_title(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/?search=Task A")

        task_titles = [task["title"] for task in response.data["results"]]

        self.assertEqual(response.status_code, 200)
        self.assertIn("Task A", task_titles)


    def test_search_tasks_by_assigned_username(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/?search=test2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)


    def test_order_tasks_by_date_created_descending(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/?ordering=-date_created")

        task_ids = [task["id"] for task in response.data["results"]]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(task_ids[1], self.taskA.id)
        self.assertEqual(task_ids[0], self.taskC.id)


    def test_order_tasks_by_date_created_ascending(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get("/tasks/?ordering=date_created")

        task_ids = [task["id"] for task in response.data["results"]]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(task_ids[1], self.taskC.id)
        self.assertEqual(task_ids[0], self.taskA.id)


    def test_pagination_limits_results(self):
        self.client.force_authenticate(user=self.userA)

        for i in range(7):
            Task.objects.create(
                title=f"Extra Task {i}",
                status="TODO",
                priority="LOW",
                created_by=self.userA
            )

        response = self.client.get("/tasks/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 9)


    def test_pagination_second_page(self):
        self.client.force_authenticate(user=self.userA)

        for i in range(7):
            Task.objects.create(
                title=f"Extra Task {i}",
                status="TODO",
                priority="LOW",
                created_by=self.userA
            )

        response = self.client.get("/tasks/?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 4)
        self.assertEqual(response.data["count"], 9)


    def test_pagination_max_page_size(self):
        self.client.force_authenticate(user=self.userA)

        for i in range(9):
            Task.objects.create(
                title=f"Extra Task {i}",
                status="TODO",
                priority="LOW",
                created_by=self.userA
            )

        response = self.client.get("/tasks/?page_size=11")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 11)


    def test_pagination_custom_page_size(self):
        self.client.force_authenticate(user=self.userA)

        for i in range(5):
            Task.objects.create(
                title=f"Extra Task {i}",
                status="TODO",
                priority="LOW",
                created_by=self.userA
            )

        response = self.client.get("/tasks/?page_size=3")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["count"], 7)


    def test_user_can_retrieve_accessible_task(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get(f"/tasks/{self.taskA.id}/")

        self.assertEqual(response.status_code, 200)

        
    def test_user_cannot_retrieve_inaccessible_task(self):
        self.client.force_authenticate(user=self.userA)
        response = self.client.get(f"/tasks/{self.taskB.id}/")

        self.assertEqual(response.status_code, 404)


    def test_user_cannot_change_task_creator(self):
        self.client.force_authenticate(user=self.userA)

        response = self.client.patch(
            f"/tasks/{self.taskA.id}/",
            {
                "created_by": self.userB.id,
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["created_by"], self.userA.id)