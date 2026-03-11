import os
import pytest

from yottaml.skywalker import SkywalkerTaskApi, TaskStatus


@pytest.mark.integration
def test_list_tasks_success_integration():
    """
    Integration test for paginated task list.
    Requires:
      - YOTTA_API_KEY
      - YOTTA_ENDPOINT_ID
    """
    api_key = os.getenv("YOTTA_API_KEY")
    endpoint_id = os.getenv("YOTTA_ENDPOINT_ID")
    base_url = os.getenv("YOTTA_BASE_URL", "https://api.yottalabs.ai")

    if not api_key or not endpoint_id:
        pytest.skip("Missing env vars")

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url)

    resp = api.list_tasks(
        endpoint_id=endpoint_id,
        status=TaskStatus.PROCESSING,
        page=1,
        page_size=5,
    )

    assert isinstance(resp, dict)
    assert resp.get("code") == 10000
    data = resp.get("data") or {}
    items = data.get("items") or []
    pagination = data.get("pagination") or {}

    assert isinstance(items, list)
    assert "page" in pagination
    assert "pageSize" in pagination
    assert "totalCount" in pagination
    assert "totalPages" in pagination


def test_list_tasks_invalid_status():
    """status must be a valid TaskStatus string."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    with pytest.raises(ValueError):
        api.list_tasks(endpoint_id=1, status="INVALID_STATUS", page=1, page_size=10)

    with pytest.raises(ValueError):
        api.list_tasks(endpoint_id=1, status="4", page=1, page_size=10)


def test_list_tasks_invalid_pagination():
    """page/pageSize must be >= 1."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    with pytest.raises(ValueError):
        api.list_tasks(endpoint_id=1, page=0, page_size=5)

    with pytest.raises(ValueError):
        api.list_tasks(endpoint_id=1, page=1, page_size=0)


def test_list_tasks_query_params(monkeypatch):
    """Verify query params and path for v2."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")
    captured = {}

    def fake_get(path, payload=None):
        captured["path"] = path
        captured["payload"] = payload or {}
        return {
            "code": 10000,
            "data": {
                "items": [],
                "pagination": {"page": 2, "pageSize": 20, "totalCount": 0, "totalPages": 0},
            },
        }

    monkeypatch.setattr(api, "http_get", fake_get)

    resp = api.list_tasks(
        endpoint_id=123,
        status=TaskStatus.SUCCESS,
        page=2,
        page_size=20,
    )

    assert resp["code"] == 10000
    assert captured["path"] == "/v2/serverless/123/tasks"
    assert captured["payload"]["status"] == TaskStatus.SUCCESS.value
    assert captured["payload"]["pageNumber"] == 2
    assert captured["payload"]["pageSize"] == 20
