import os
import pytest
from yottaml.error import ParameterRequiredError
from yottaml.skywalker import SkywalkerTaskApi


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
    assert data.get("taskId") == task_id


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

    with pytest.raises(ParameterRequiredError):
        api.get_task(endpoint_id=1, task_id="")


def test_get_task_path(monkeypatch):
    """Verify request path for v2."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")
    captured = {}

    def fake_get(path):
        captured["path"] = path
        return {"code": 10000, "data": {}}

    monkeypatch.setattr(api, "http_get", fake_get)

    api.get_task(endpoint_id=123, task_id="task_abc")

    assert captured["path"] == "/v2/serverless/123/tasks/task_abc"
