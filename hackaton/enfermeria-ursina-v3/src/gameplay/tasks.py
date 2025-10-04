class Task:
    def __init__(self, task_id: str, title: str, requires: list[str] | None = None):
        self.id = task_id
        self.title = title
        self.done = False
        self.requires = requires or []

class TaskManager:
    def __init__(self, tasks: list[Task]):
        self.tasks = tasks
        self.current_index = 0

    def can_complete(self, task_id: str) -> bool:
        t = self._get(task_id)
        return bool(t) and all(self._get(r).done for r in t.requires)

    def complete(self, task_id: str) -> bool:
        if not self.can_complete(task_id):
            return False
        t = self._get(task_id)
        if t and not t.done:
            t.done = True
            self.current_index = min(self.tasks.index(t) + 1, len(self.tasks) - 1)
            return True
        return False

    def progress(self) -> tuple[int, int]:
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.done)
        return done, total

    def all_done(self) -> bool:
        return all(t.done for t in self.tasks)

    def _get(self, task_id: str):
        return next((t for t in self.tasks if t.id == task_id), None)
