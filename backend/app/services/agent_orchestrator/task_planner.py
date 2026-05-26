class TaskPlanner:
    """Small placeholder for the one-click application plan planner."""

    def build_portal_tasks(self, program_ids: list[int]) -> list[dict]:
        return [{"program_id": program_id, "task_type": "fill_portal", "status": "pending"} for program_id in program_ids]
