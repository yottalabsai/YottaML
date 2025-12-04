import os
import time
import pytest

from yotta.skywalker import SkywalkerTaskApi


@pytest.mark.integration
def test_create_task_success_integration():
    """
    Integration test for creating a task.
    Requires environment variables:
      - YOTTA_API_KEY
      - YOTTA_ENDPOINT_ID
    """
    api_key = os.getenv("YOTTA_API_KEY")
    endpoint_id = os.getenv("YOTTA_ENDPOINT_ID")
    base_url = os.getenv("YOTTA_BASE_URL", "https://api.yottalabs.ai")

    if not api_key or not endpoint_id:
        pytest.skip("Missing YOTTA_API_KEY or YOTTA_ENDPOINT_ID")

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url)

    user_task_id = f"test_{int(time.time())}"

    payload = {
        "temperature": 0.5,
        "top_p": 0.9,
        "max_tokens": 64,
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [{"role": "user", "content": "ping"}],
        "stream": False,
    }

    resp = api.create_task(
        endpoint_id=endpoint_id,
        user_task_id=user_task_id,
        worker_port=8000,
        process_uri="/v1/chat/completions",
        task_data=payload,
    )

    assert isinstance(resp, dict)
    assert resp.get("code") == 10000
    assert resp.get("data", {}).get("userTaskId") == user_task_id


def test_create_task_invalid_user_task_id():
    """Test invalid userTaskId patterns (allowed: letters, numbers, underscores)."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    # invalid characters
    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            user_task_id="bad-id-!",
            worker_port=8000,
            process_uri="/v1/chat/completions",
            task_data={"foo": "bar"},
        )

    # too long (>255)
    too_long = "a" * 256
    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            user_task_id=too_long,
            worker_port=8000,
            process_uri="/v1/chat/completions",
            task_data={"foo": "bar"},
        )


def test_create_task_invalid_port_and_url():
    """Test workerPort range and notifyUrl format validation."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            user_task_id="task_1",
            worker_port=0,
            process_uri="/v1/chat/completions",
            task_data={"foo": "bar"},
        )

    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            user_task_id="task_1",
            worker_port=70000,
            process_uri="/v1/chat/completions",
            task_data={"foo": "bar"},
        )

    # invalid notifyUrl
    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            user_task_id="task_1",
            worker_port=8000,
            process_uri="/v1/chat/completions",
            notify_url="invalid-url",
            task_data={"foo": "bar"},
        )


def test_create_task_header_and_process_uri_normalized(monkeypatch):
    """
    Test:
      - processUri auto-normalizes (adds leading '/')
      - X-Endpoint-ID header correctly applied
      - header with valid structure is passed through
    """
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    captured = {}

    def fake_post(path, payload, headers=None):
        captured["path"] = path
        captured["payload"] = payload
        captured["headers"] = headers or {}
        return {"code": 10000, "data": {"userTaskId": payload["userTaskId"]}}

    monkeypatch.setattr(api, "http_post", fake_post)

    resp = api.create_task(
        endpoint_id=123456,
        user_task_id="task_abc",
        worker_port=8000,
        process_uri="v1/chat/completions",  # without leading slash
        task_data={"foo": "bar"},
        header={"X-Request-ID": "req-1"},
    )

    assert resp["code"] == 10000
    assert captured["path"] == "/openapi/v1/skywalker/tasks/create"
    assert captured["payload"]["processUri"] == "/v1/chat/completions"
    assert captured["headers"]["X-Endpoint-ID"] == "123456"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["payload"]["header"]["X-Request-ID"] == "req-1"
