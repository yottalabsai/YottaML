import os
import pytest

from yottaml.skywalker import SkywalkerTaskApi


@pytest.mark.integration
def test_get_processing_count_success_integration():
    """
    Integration test for retrieving processing task count.
    Requires:
      - YOTTA_API_KEY
      - YOTTA_ENDPOINT_ID
    """
    api_key = os.getenv("YOTTA_API_KEY")
    endpoint_id = os.getenv("YOTTA_ENDPOINT_ID")
    base_url = os.getenv("YOTTA_BASE_URL", "https://api.yottalabs.ai")

    if not api_key or not endpoint_id:
        pytest.skip("Missing YOTTA_API_KEY or YOTTA_ENDPOINT_ID")

    api = SkywalkerTaskApi(api_key=api_key, base_url=base_url)

    resp = api.get_processing_count(endpoint_id=endpoint_id)

    assert isinstance(resp, dict)
    assert resp.get("code") == 10000


def test_get_processing_count_invalid_endpoint_id():
    """endpoint_id must be > 0."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    with pytest.raises(ValueError):
        api.get_processing_count(endpoint_id=0)

    with pytest.raises(ValueError):
        api.get_processing_count(endpoint_id=-10)


def test_get_processing_count_path(monkeypatch):
    """Verify request path for v2."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")
    captured = {}

    def fake_get(path):
        captured["path"] = path
        return {"code": 10000, "data": {"processing": 0}}

    monkeypatch.setattr(api, "http_get", fake_get)

    api.get_processing_count(endpoint_id=999)

    assert captured["path"] == "/v2/serverless/999/tasks/count"


def test_get_processing_count_response_structure(monkeypatch):
    """Check response format consistency."""
    api = SkywalkerTaskApi(api_key="dummy", base_url="http://localhost")

    monkeypatch.setattr(
        api,
        "http_get",
        lambda path: {
            "code": 10000,
            "message": "success",
            "data": {"processing": 5},
        },
    )

    resp = api.get_processing_count(endpoint_id=1)
    assert resp["code"] == 10000
    assert resp["data"]["processing"] == 5
