import os
import time
import pytest

from yottaml.skywalker import SkywalkerTaskApi


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

    task_id = f"test_{int(time.time())}"

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
        task_id=task_id,
        worker_port=8000,
        process_uri="/v1/chat/completions",
        input=payload,
    )

    assert isinstance(resp, dict)
    assert resp.get("code") == 10000
    assert resp.get("data", {}).get("taskId") == task_id


def test_create_task_invalid_task_id():
    """Test invalid taskId patterns (allowed: letters, numbers, underscores)."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    # invalid characters
    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            task_id="bad-id-!",
            worker_port=8000,
            process_uri="/v1/chat/completions",
            input={"foo": "bar"},
        )

    # too long (>255)
    too_long = "a" * 256
    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            task_id=too_long,
            worker_port=8000,
            process_uri="/v1/chat/completions",
            input={"foo": "bar"},
        )


def test_create_task_invalid_port_and_webhook():
    """Test workerPort range and webhook URL format validation."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            task_id="task_1",
            worker_port=0,
            process_uri="/v1/chat/completions",
            input={"foo": "bar"},
        )

    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            task_id="task_1",
            worker_port=70000,
            process_uri="/v1/chat/completions",
            input={"foo": "bar"},
        )

    # invalid webhook URL
    with pytest.raises(ValueError):
        api.create_task(
            endpoint_id=1,
            task_id="task_1",
            worker_port=8000,
            process_uri="/v1/chat/completions",
            webhook="invalid-url",
            input={"foo": "bar"},
        )


def test_create_task_process_uri_normalized(monkeypatch):
    """
    Test:
      - processUri auto-normalizes (adds leading '/')
      - correct path is used (/v2/serverless/{id}/tasks)
      - headers kwarg is passed through in payload
    """
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    captured = {}

    def fake_post(path, payload):
        captured["path"] = path
        captured["payload"] = payload
        return {"code": 10000, "data": {"taskId": payload.get("taskId")}}

    monkeypatch.setattr(api, "http_post", fake_post)

    resp = api.create_task(
        endpoint_id=123456,
        task_id="task_abc",
        worker_port=8000,
        process_uri="v1/chat/completions",  # without leading slash
        input={"foo": "bar"},
        headers={"X-Request-ID": "req-1"},
    )

    assert resp["code"] == 10000
    assert captured["path"] == "/v2/serverless/123456/tasks"
    assert captured["payload"]["processUri"] == "/v1/chat/completions"
    assert captured["payload"]["headers"]["X-Request-ID"] == "req-1"
