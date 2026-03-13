import pytest
from unittest.mock import patch
from yottaml.gpu import GpuApi
from yottaml.error import ClientError


@pytest.fixture
def gpu_api():
    return GpuApi(api_key="fake_api_key", base_url="https://api.test.yottalabs.ai")


def test_gpu_list_success(gpu_api):
    mock_response = {
        "code": 10000,
        "message": "success",
        "data": [{"gpuType": "RTX_4090_24G", "regions": ["us-east-1"]}],
    }

    with patch.object(gpu_api, "http_get", return_value=mock_response) as mock_get:
        resp = gpu_api.get_gpus()
        assert resp == mock_response
        mock_get.assert_called_once_with("/v2/vms/types")
        assert resp["data"][0]["gpuType"] == "RTX_4090_24G"


def test_gpu_list_client_error(gpu_api):
    with patch.object(
        gpu_api,
        "http_get",
        side_effect=ClientError(400, 40001, "Bad Request", {}, None),
    ):
        with pytest.raises(ClientError) as exc:
            gpu_api.get_gpus()
        assert exc.value.status_code == 400
        assert exc.value.error_code == 40001


def test_gpu_list_unexpected_response_code(gpu_api):
    mock_resp = {"code": 9999, "message": "internal error", "data": None}
    with patch.object(gpu_api, "http_get", return_value=mock_resp):
        resp = gpu_api.get_gpus()
        assert resp["code"] != 10000
        assert "internal" in resp["message"].lower()
