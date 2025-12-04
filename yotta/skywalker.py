# yotta/skywalker.py
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

from yotta import API
from yotta.lib.enums import TaskStatus, ResultSendStatus
from yotta.lib.utils import (
    check_required_parameter,
    check_is_positive_int,
    clean_none_value,
)

# ---------------------------------------------------------------------------
# Validators (mirror your doc; raise ValueError on violations)
# ---------------------------------------------------------------------------

_USER_TASK_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _validate_user_task_id(v: str) -> None:
    check_required_parameter(v, "userTaskId")
    if len(v) > 255:
        raise ValueError("userTaskId exceeds maximum length of 255 characters")
    if not _USER_TASK_ID_RE.match(v):
        raise ValueError("userTaskId can only contain letters, numbers, and underscores")


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
    # relaxed path char check; backend will do strict validation
    if not re.match(r"^/[A-Za-z0-9._~!$&'()*+,;=:@/\-]*$", uri):
        raise ValueError("processUri contains invalid characters for URI path")
    return uri


def _validate_notify_url(u: Optional[str]) -> None:
    if not u:
        return
    if len(u) > 512:
        raise ValueError("notifyUrl exceeds maximum length of 512 characters")
    p = urlparse(u)
    if not (p.scheme in ("http", "https") and p.netloc):
        raise ValueError("notifyUrl must be a valid URL")


def _validate_notify_auth_key(v: Optional[str]) -> None:
    if v is None:
        return
    if len(v) > 255:
        raise ValueError("notifyAuthKey exceeds maximum length of 255 characters")


def _validate_task_data(d: Any) -> None:
    if d is None:
        raise ValueError("taskData is required")
    if isinstance(d, (dict, list, tuple, str)) and len(d) == 0:
        raise ValueError("taskData cannot be empty")


def _validate_header(h: Optional[Dict[str, str]]) -> None:
    if h is None:
        return
    if not isinstance(h, dict):
        raise ValueError("header must be a kv structure")
    for k, v in h.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError("header must be a kv structure of string->string")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class SkywalkerTaskApi(API):
    """
    Python client for Elastic Task module (OpenAPI v1).

    Endpoints:
      1) Create Task
         POST /openapi/v1/skywalker/tasks/create

      2) Get Task Detail
         GET  /openapi/v1/skywalker/tasks/{id}

      3) Get Processing Count
         GET  /openapi/v1/skywalker/tasks/processing/count

      4) List Tasks (paged)
         GET  /openapi/v1/skywalker/tasks

    Required headers:
      - X-API-Key      : provided by API base
      - X-Endpoint-ID  : required per request (Elastic Deployment id)
      - Content-Type   : application/json (for POST)
    """

    # ----------------------------- 1) Create Task -----------------------------
    def create_task(
        self,
        *,
        endpoint_id: Union[int, str],
        user_task_id: str,
        worker_port: int,
        process_uri: str,
        task_data: Any,
        notify_url: Optional[str] = None,
        notify_auth_key: Optional[str] = None,
        header: Optional[Dict[str, str]] = None,
    ):
        """
        Create a task and submit it to the elastic queue
        (idempotent on userTaskId within the same endpoint).

        POST /openapi/v1/skywalker/tasks/create

        Headers:
          X-Endpoint-ID : required (this method's `endpoint_id`)
          Content-Type  : application/json

        Request body (CreateTaskRequest):
          - userTaskId     : string, required, <=255, ^[A-Za-z0-9_]+$
          - workerPort     : int, required, 1..65535
          - processUri     : string, required, <=255, no spaces, leading "/" enforced
          - notifyUrl      : string, optional, <=512, valid URL
          - notifyAuthKey  : string, optional, <=255
          - taskData       : any json (object/array/string), required, non-empty
          - header         : dict[str,str], optional (forwarded headers to worker)

        Returns:
          JSON dict containing standard response envelope (code/message/data).
        """
        # validate
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")
        _validate_user_task_id(user_task_id)
        _validate_worker_port(worker_port)
        process_uri = _normalize_and_validate_process_uri(process_uri)
        _validate_notify_url(notify_url)
        _validate_notify_auth_key(notify_auth_key)
        _validate_task_data(task_data)
        _validate_header(header)

        payload = clean_none_value(
            {
                "userTaskId": user_task_id,
                "workerPort": worker_port,
                "processUri": process_uri,
                "notifyUrl": notify_url,
                "notifyAuthKey": notify_auth_key,
                "taskData": task_data,
                "header": header,
            }
        )

        headers = {
            "X-Endpoint-ID": str(int(endpoint_id)),
            "Content-Type": "application/json",
        }
        return self.http_post("/openapi/v1/skywalker/tasks/create", payload, headers=headers)

    # ----------------------------- 2) Get Task Detail -----------------------------
    def get_task(
        self,
        *,
        endpoint_id: Union[int, str],
        task_id: Union[int, str],
    ):
        """
        Get task detail.

        GET /openapi/v1/skywalker/tasks/{id}

        Headers:
          X-Endpoint-ID : required

        Returns:
          JSON dict with TaskDTO, including fields such as:
            - userTaskId
            - workerUrl
            - notifyUrl
            - timestamps
            - status
            - failedReason
            - resultSendStatus
            - resultSendCount
            - nextResultSendTime
            - taskData
            - header
            - taskResult
            - notifySendCount
            - lastNotifiedAt
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")
        check_required_parameter(task_id, "task_id")

        headers = {"X-Endpoint-ID": str(int(endpoint_id))}
        return self.http_get(f"/openapi/v1/skywalker/tasks/{task_id}", headers=headers)

    # ----------------------------- 3) Get Processing Count -----------------------------
    def get_processing_count(self, *, endpoint_id: Union[int, str]):
        """
        Get number of tasks currently queued + processing for the endpoint.

        GET /openapi/v1/skywalker/tasks/processing/count

        Headers:
          X-Endpoint-ID : required

        Returns:
          JSON dict:
            {
              "code": 10000,
              "message": "success",
              "data": {
                "processingCount": <int>
              }
            }
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")

        headers = {"X-Endpoint-ID": str(int(endpoint_id))}
        return self.http_get("/openapi/v1/skywalker/tasks/processing/count", headers=headers)

    # ----------------------------- 4) List Tasks (paged) -----------------------------
    def list_tasks(
        self,
        *,
        endpoint_id: Union[int, str],
        status: Optional[Union[int, TaskStatus]] = None,
        page: int = 1,
        page_size: int = 10,
    ):
        """
        List tasks with pagination and optional status filter.

        GET /openapi/v1/skywalker/tasks

        Query parameters:
          - status   : optional, 0..3  (PROCESSING=0, DELIVERED=1, SUCCESS=2, FAILED=3)
          - page     : default 1 (>=1)
          - pageSize : default 10 (>=1)

        Headers:
          X-Endpoint-ID : required

        Returns:
          JSON dict:
            {
              "code": 10000,
              "message": "success",
              "data": {
                "items": [PageTaskDTO...],
                "pagination": {
                  "page": <int>,
                  "pageSize": <int>,
                  "totalCount": <int>,
                  "totalPages": <int>
                }
              }
            }
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")

        # normalize & validate status
        status_val: Optional[int] = None
        if status is not None:
            status_val = int(status)
            if status_val < 0 or status_val > 3:
                raise ValueError("status must be between 0 and 3")

        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("pageSize must be >= 1")

        params = clean_none_value(
            {
                "status": status_val,
                "page": page,
                "pageSize": page_size,
            }
        )

        headers = {"X-Endpoint-ID": str(int(endpoint_id))}
        return self.http_get("/openapi/v1/skywalker/tasks", payload=params, headers=headers)

    # ----------------------------- Notification payload checker (optional) -----------------------------
    @staticmethod
    def validate_notify_payload(payload: Dict[str, Any]) -> None:
        """
        Optional helper to validate NotifyRequestBody shape (client-side sanity check only).

        This does not perform any network calls; it only validates the shape
        of the notification payload received from Skywalker.

        Required fields:
          - task_id      : int
          - user_task_id : string (<=255, ^[A-Za-z0-9_]+$)
          - endpoint_id  : string (<=255)
          - status       : "Success" | "Failed"
          - success      : bool
          - timestamp    : string (format not strictly enforced here)
          - retry_count  : int >= 1

        Optional fields:
          - result        : object (any JSON-serializable value)
          - failed_reason : string (when status is "Failed")

        Raises:
          ValueError if the payload shape is invalid or violates constraints.
        """
        if not isinstance(payload, dict):
            raise ValueError("notify payload must be a JSON object")

        # task_id
        if "task_id" not in payload:
            raise ValueError("task_id is required")
        if not isinstance(payload["task_id"], int):
            raise ValueError("task_id must be integer")

        # user_task_id
        if "user_task_id" not in payload:
            raise ValueError("user_task_id is required")
        _validate_user_task_id(str(payload["user_task_id"]))

        # endpoint_id
        if "endpoint_id" not in payload:
            raise ValueError("endpoint_id is required")
        eid = str(payload["endpoint_id"])
        if len(eid) > 255:
            raise ValueError("endpoint_id exceeds maximum length of 255 characters")

        # status & success
        st = payload.get("status")
        if st not in ("Success", "Failed"):
            raise ValueError("status must be 'Success' or 'Failed'")
        if not isinstance(payload.get("success"), bool):
            raise ValueError("success must be boolean")

        # timestamp (format not enforced strictly; backend provides ISO-like string)
        if "timestamp" not in payload or not str(payload["timestamp"]).strip():
            raise ValueError("timestamp is required")

        # retry_count
        if "retry_count" not in payload:
            raise ValueError("retry_count is required")
        try:
            rc = int(payload["retry_count"])
        except Exception:
            raise ValueError("retry_count must be integer")
        if rc < 1:
            raise ValueError("retry_count must be >= 1")

        # result (optional): any JSON; failed_reason (optional): string
        if "failed_reason" in payload and payload["failed_reason"] is not None:
            if not isinstance(payload["failed_reason"], str):
                raise ValueError("failed_reason must be string when present")
