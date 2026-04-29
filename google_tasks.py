"""
services/google_tasks.py
────────────────────────
Async wrapper around the Google Tasks REST API v1.
Handles task creation, listing, and deletion per authenticated user.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import httpx

from services.oauth import get_credentials

logger = logging.getLogger(__name__)

TASKS_API = "https://tasks.googleapis.com/tasks/v1"


class GoogleTasksService:
    """
    Per-user Google Tasks client.

    Usage:
        service = GoogleTasksService(user_id=12345)
        task_id = await service.create_task("Doctor appointment", due_datetime)
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self._creds = None

    async def _get_headers(self) -> dict:
        """Build Authorization headers, refreshing token if needed."""
        if not self._creds:
            self._creds = get_credentials(self.user_id)  # raises if not connected
        return {
            "Authorization": f"Bearer {self._creds.token}",
            "Content-Type": "application/json",
        }

    async def create_task(
        self,
        title: str,
        due: Optional[datetime] = None,
        notes: str = "",
    ) -> str:
        """
        Create a new task in the user's default task list.

        Args:
            title: Task title (extracted by NLP parser)
            due:   Python datetime object for the due date
            notes: Optional extra notes

        Returns:
            str: Google Tasks task ID (e.g. "MTc4MDY3MDU3NzQ0NjE3NzY4OTI6MDo0")
        """
        tasklist_id = await self._get_default_tasklist()

        # Google Tasks API expects RFC 3339 format with Z suffix
        due_str = None
        if due:
            # Ensure UTC
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            due_str = due.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        payload = {"title": title, "notes": notes}
        if due_str:
            payload["due"] = due_str

        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TASKS_API}/lists/{tasklist_id}/tasks",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            task = resp.json()

        logger.info("Task created: %s (id=%s)", title, task["id"])
        return task["id"]

    async def list_tasks(self, max_results: int = 10) -> List[dict]:
        """
        Retrieve upcoming tasks for the user.

        Returns:
            List of task dicts with keys: id, title, due, status
        """
        tasklist_id = await self._get_default_tasklist()
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{TASKS_API}/lists/{tasklist_id}/tasks",
                headers=headers,
                params={
                    "maxResults": max_results,
                    "showCompleted": False,
                    "showDeleted": False,
                    "orderBy": "dueDate",
                },
            )
            resp.raise_for_status()

        items = resp.json().get("items", [])
        return [
            {
                "id": t["id"],
                "title": t.get("title", "Untitled"),
                "due": t.get("due", "—"),
                "status": t.get("status", "needsAction"),
            }
            for t in items
        ]

    async def delete_task(self, task_id: str) -> None:
        """Delete a task by its ID."""
        tasklist_id = await self._get_default_tasklist()
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{TASKS_API}/lists/{tasklist_id}/tasks/{task_id}",
                headers=headers,
            )
            resp.raise_for_status()

        logger.info("Task deleted: %s", task_id)

    # ── Private ─────────────────────────────────────────────────────────────

    async def _get_default_tasklist(self) -> str:
        """Fetch ID of the user's primary task list (@default)."""
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{TASKS_API}/users/@me/lists",
                headers=headers,
                params={"maxResults": 1},
            )
            resp.raise_for_status()

        lists = resp.json().get("items", [])
        if not lists:
            raise RuntimeError("No task lists found for user.")
        return lists[0]["id"]
