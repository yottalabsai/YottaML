import os
import pytest
from yotta.error import ParameterRequiredError
from yotta.skywalker import SkywalkerTaskApi


@pytest.mark.integration
def test_get_task_success_integration():
    """
    Integration test for retrieving one task.
    Requires:
      - YOTTA_API_KEY
      - YOTTA_ENDPOINT_ID
      - YOTTA_TASK_ID
    """
    api_key = os.getenv("YOTTA_API_KEY")
    endpoint_id = os.getenv("YOTTA_ENDPOINT_ID")
    task_id = os.getenv("YOTTA_TASK_ID")
    base_url = os.getenv("YOTTA_BASE_URL", "https://api.yottalabs.ai")

    if not api_key or not endpoint_id or not task_id:
        pytest.skip("Missing required environment variables.")

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url)

    resp = api.get_task(endpoint_id=endpoint_id, task_id=task_id)

    assert isinstance(resp, dict)
    assert resp.get("code") == 10000
    data = resp.get("data") or {}
    assert data.get("userTaskId") == task_id


def test_get_task_invalid_endpoint_id():
    """endpoint_id must be a positive integer."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    with pytest.raises(ValueError):
        api.get_task(endpoint_id=0, task_id="task_x")

    with pytest.raises(ValueError):
        api.get_task(endpoint_id=-5, task_id="task_x")


def test_get_task_empty_task_id():
    """task_id must not be empty."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    # empty string still matches type (str) but should fail "required" check
    with pytest.raises(ParameterRequiredError):
        api.get_task(endpoint_id=1, task_id="")


def test_get_task_headers_and_path(monkeypatch):
    """Verify request path and X-Endpoint-ID header."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")
    captured = {}

    def fake_get(path, headers=None):
        captured["path"] = path
        captured["headers"] = headers or {}
        return {"code": 10000, "data": {}}

    monkeypatch.setattr(api, "http_get", fake_get)

    api.get_task(endpoint_id=123, task_id="task_abc")

    assert captured["path"] == "/openapi/v1/skywalker/tasks/task_abc"
    assert captured["headers"]["X-Endpoint-ID"] == "123"
