# yotta/skywalker.py
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

from yottaml import API
from yottaml.lib.enums import TaskStatus, ResultSendStatus
from yottaml.lib.utils import (
    check_required_parameter,
    check_is_positive_int,
    clean_none_value,
)

# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

_TASK_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _validate_task_id(v: Optional[str]) -> None:
    if not v:
        return
    if len(v) > 255:
        raise ValueError("taskId exceeds maximum length of 255 characters")
    if not _TASK_ID_RE.match(v):
        raise ValueError("taskId can only contain letters, numbers, and underscores")


def _validate_worker_port(port: int) -> None:
    check_required_parameter(port, "workerPort")
    if port < 1:
        raise ValueError("workerPort must be at least 1")
    if port > 65535:
        raise ValueError("workerPort must not exceed 65535")


def _normalize_and_validate_process_uri(uri: str) -> str:
    check_required_parameter(uri, "processUri")
    if " " in uri:
        raise ValueError("processUri must not contain spaces")
    if len(uri) > 255:
        raise ValueError("processUri exceeds maximum length of 255 characters")
    if not uri.startswith("/"):
        uri = "/" + uri
    if not re.match(r"^/[A-Za-z0-9._~!$&'()*+,;=:@/\-]*$", uri):
        raise ValueError("processUri contains invalid characters for URI path")
    return uri


def _validate_webhook(u: Optional[str]) -> None:
    if not u:
        return
    if len(u) > 512:
        raise ValueError("webhook exceeds maximum length of 512 characters")
    p = urlparse(u)
    if not (p.scheme in ("http", "https") and p.netloc):
        raise ValueError("webhook must be a valid URL")


def _validate_webhook_auth_key(v: Optional[str]) -> None:
    if v is None:
        return
    if len(v) > 255:
        raise ValueError("webhookAuthKey exceeds maximum length of 255 characters")


def _validate_input(d: Any) -> None:
    if d is None:
        raise ValueError("input is required")
    if isinstance(d, (dict, list, tuple, str)) and len(d) == 0:
        raise ValueError("input cannot be empty")


def _validate_headers(h: Optional[Dict[str, str]]) -> None:
    if h is None:
        return
    if not isinstance(h, dict):
        raise ValueError("headers must be a kv structure")
    for k, v in h.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError("headers must be a kv structure of string->string")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class SkywalkerTaskApi(API):
    """
    Python client for Serverless Task API (OpenAPI v2).

    Endpoints (all scoped under a serverless endpoint):
      1) Submit Task
         POST /v2/serverless/{id}/tasks

      2) Get Task Detail
         GET  /v2/serverless/{id}/tasks/{taskId}

      3) Get Task Count
         GET  /v2/serverless/{id}/tasks/count

      4) List Tasks (paged)
         GET  /v2/serverless/{id}/tasks
    """

    # ----------------------------- 1) Submit Task -----------------------------
    def create_task(
        self,
        *,
        endpoint_id: Union[int, str],
        worker_port: int,
        process_uri: str,
        input: Any,
        task_id: Optional[str] = None,
        webhook: Optional[str] = None,
        webhook_auth_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Submit a task to a QUEUE-mode serverless endpoint.

        POST /v2/serverless/{id}/tasks

        Args:
            endpoint_id (int|str): Serverless endpoint ID.
            worker_port (int): Worker port (1-65535).
            process_uri (str): Process URI on the worker (max 255 chars).
            input (any): Task input data (required, non-empty JSON).
            task_id (str, optional): User-defined task ID (alphanumeric + underscore, max 255).
                Auto-generated UUID if omitted.
            webhook (str, optional): Webhook URL for async result delivery (max 512 chars).
            webhook_auth_key (str, optional): Webhook authentication key (max 255 chars).
            headers (dict, optional): Headers to forward with the task request.

        Returns:
            JSON dict: {"code": 10000, "data": {"taskId": "..."}}
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")
        _validate_task_id(task_id)
        _validate_worker_port(worker_port)
        process_uri = _normalize_and_validate_process_uri(process_uri)
        _validate_webhook(webhook)
        _validate_webhook_auth_key(webhook_auth_key)
        _validate_input(input)
        _validate_headers(headers)

        payload = clean_none_value(
            {
                "taskId": task_id,
                "workerPort": worker_port,
                "processUri": process_uri,
                "webhook": webhook,
                "webhookAuthKey": webhook_auth_key,
                "input": input,
                "headers": headers,
            }
        )

        return self.http_post(f"/v2/serverless/{int(endpoint_id)}/tasks", payload)

    # ----------------------------- 2) Get Task Detail -----------------------------
    def get_task(
        self,
        *,
        endpoint_id: Union[int, str],
        task_id: Union[int, str],
    ):
        """
        Get task detail.

        GET /v2/serverless/{id}/tasks/{taskId}

        Args:
            endpoint_id (int|str): Serverless endpoint ID.
            task_id (str): Task ID.

        Returns:
            JSON dict with task details.
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")
        check_required_parameter(task_id, "task_id")

        return self.http_get(f"/v2/serverless/{int(endpoint_id)}/tasks/{task_id}")

    # ----------------------------- 3) Get Task Count -----------------------------
    def get_processing_count(self, *, endpoint_id: Union[int, str]):
        """
        Get number of tasks currently processing for the endpoint.

        GET /v2/serverless/{id}/tasks/count

        Args:
            endpoint_id (int|str): Serverless endpoint ID.

        Returns:
            JSON dict:
              {
                "code": 10000,
                "message": "success",
                "data": {"processing": <int>}
              }
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")

        return self.http_get(f"/v2/serverless/{int(endpoint_id)}/tasks/count")

    # ----------------------------- 4) List Tasks (paged) -----------------------------
    def list_tasks(
        self,
        *,
        endpoint_id: Union[int, str],
        status: Optional[Union[str, TaskStatus]] = None,
        page: int = 1,
        page_size: int = 10,
    ):
        """
        List tasks with pagination and optional status filter.

        GET /v2/serverless/{id}/tasks

        Query parameters:
          - status     : optional, PROCESSING | DELIVERED | SUCCESS | FAILED
          - pageNumber : default 1 (>=1)
          - pageSize   : default 10 (>=1)

        Args:
            endpoint_id (int|str): Serverless endpoint ID.
            status (str|TaskStatus, optional): Filter by task status.
            page (int): Page number (default 1).
            page_size (int): Items per page (default 10).

        Returns:
            JSON dict with paginated task list.
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")

        status_val: Optional[str] = None
        if status is not None:
            if isinstance(status, TaskStatus):
                status_val = status.value
            elif isinstance(status, str) and status.upper() in TaskStatus.__members__:
                status_val = status.upper()
            else:
                valid = list(TaskStatus.__members__.keys())
                raise ValueError(f"status must be one of {valid}")

        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("pageSize must be >= 1")

        params = clean_none_value(
            {
                "status": status_val,
                "pageNumber": page,
                "pageSize": page_size,
            }
        )

        return self.http_get(
            f"/v2/serverless/{int(endpoint_id)}/tasks",
            payload=params,
        )

    # ----------------------------- Notification payload checker (optional) -----------------------------
    @staticmethod
    def validate_notify_payload(payload: Dict[str, Any]) -> None:
        """
        Optional helper to validate webhook notification payload shape (client-side only).

        Required fields:
          - task_id      : int
          - user_task_id : string (<=255, ^[A-Za-z0-9_]+$)
          - endpoint_id  : string (<=255)
          - status       : "Success" | "Failed"
          - success      : bool
          - timestamp    : string
          - retry_count  : int >= 1
        """
        if not isinstance(payload, dict):
            raise ValueError("notify payload must be a JSON object")

        if "task_id" not in payload:
            raise ValueError("task_id is required")
        if not isinstance(payload["task_id"], int):
            raise ValueError("task_id must be integer")

        if "user_task_id" not in payload:
            raise ValueError("user_task_id is required")
        _validate_task_id(str(payload["user_task_id"]))

        if "endpoint_id" not in payload:
            raise ValueError("endpoint_id is required")
        eid = str(payload["endpoint_id"])
        if len(eid) > 255:
            raise ValueError("endpoint_id exceeds maximum length of 255 characters")

        st = payload.get("status")
        if st not in ("Success", "Failed"):
            raise ValueError("status must be 'Success' or 'Failed'")
        if not isinstance(payload.get("success"), bool):
            raise ValueError("success must be boolean")

        if "timestamp" not in payload or not str(payload["timestamp"]).strip():
            raise ValueError("timestamp is required")

        if "retry_count" not in payload:
            raise ValueError("retry_count is required")
        try:
            rc = int(payload["retry_count"])
        except Exception:
            raise ValueError("retry_count must be integer")
        if rc < 1:
            raise ValueError("retry_count must be >= 1")

        if "failed_reason" in payload and payload["failed_reason"] is not None:
            if not isinstance(payload["failed_reason"], str):
                raise ValueError("failed_reason must be string when present")
