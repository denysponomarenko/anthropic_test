class Task:
    def __init__(self, task_id, priority, created_at):
        self.task_id = task_id
        self.priority = priority
        self.created_at = created_at
        self.user = None
        self.deadline = None
        self.completed = False


class TaskTracker:
    def __init__(self):
        self.tasks = {}

    def add(self, timestamp, task_id, priority):
        if task_id in self.tasks:
            return False

        self.tasks[task_id] = Task(task_id, priority, timestamp)
        return True

    def update_priority(self, timestamp, task_id, priority):
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.priority = priority
        return True

    def get(self, timestamp, task_id):
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "id": task.task_id,
            "priority": task.priority,
            "user": task.user,
            "deadline": task.deadline,
            "completed": task.completed,
        }

    def search(self, timestamp, prefix):
        matches = [
            task for task in self.tasks.values()
            if task.task_id.startswith(prefix)
        ]

        matches.sort(
            key=lambda task: (-task.priority, task.created_at)
        )

        return [task.task_id for task in matches]

    def assign(self, timestamp, user, task_id, deadline):
        task = self.tasks.get(task_id)

        if not task:
            return False

        if task.user is not None:
            return False

        task.user = user
        task.deadline = deadline
        task.completed = False

        return True

    def complete(self, timestamp, user, task_id):
        task = self.tasks.get(task_id)

        if not task:
            return False

        if task.user is None:
            return False

        if task.user != user:
            return False

        # Completion must happen on or before the deadline.
        if timestamp > task.deadline:
            return False

        task.completed = True

        # Completed tasks are no longer assigned.
        task.user = None
        task.deadline = None

        return True

    def get_overdue(self, timestamp):
        result = []

        for task in self.tasks.values():
            if (
                task.user is not None
                and not task.completed
                and task.deadline < timestamp
            ):
                result.append(task.task_id)

        return sorted(result)
