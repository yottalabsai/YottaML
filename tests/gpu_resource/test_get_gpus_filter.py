import pytest
from unittest.mock import patch
from yotta.gpu_resource import GpuResourceApi
from yotta.error import ClientError
from yotta.error import ParameterRequiredError


@pytest.fixture
def gpu_api():
    """创建一个 GpuResourceApi 实例"""
    return GpuResourceApi(api_key="fake_api_key", base_url="https://api.test.yottalabs.ai")
def test_gpu_type_filter_success(gpu_api):
    """测试 gpu_type_filter 正常返回"""
    mock_response = {
        "code": 10000,
        "message": "success",
        "data": {"gpuType": "NVIDIA_A100", "memory": "80GB"}
    }
    payload = {"region": "us-east-1", "gpuBrand": "NVIDIA"}

    with patch.object(gpu_api, "http_post", return_value=mock_response) as mock_post:
        resp = gpu_api.get_gpus_filter(payload)
        assert resp == mock_response
        mock_post.assert_called_once_with("/api/resource/gpu/type/filter", payload=payload)
        assert resp["data"]["gpuType"] == "NVIDIA_A100"

def test_gpu_type_filter_missing_param(gpu_api):
    """测试参数缺失异常"""
    with pytest.raises((ValueError, ParameterRequiredError)):
        gpu_api.get_gpus_filter(None)

def test_gpu_type_filter_empty_response(gpu_api):
    """测试 data 为空时处理"""
    mock_resp = {"code": 10000, "message": "success", "data": None}
    with patch.object(gpu_api, "http_post", return_value=mock_resp):
        resp = gpu_api.get_gpus_filter({"region": "sg"})
        assert resp["data"] is None


def test_gpu_type_filter_http_error(gpu_api):
    """测试 HTTP 异常返回"""
    with patch.object(gpu_api, "http_post", side_effect=ClientError(500, 50000, "ServerError", {}, None)):
        with pytest.raises(ClientError) as exc:
            gpu_api.get_gpus_filter({"region": "us"})
        assert exc.value.error_code == 50000
        assert "Server" in str(exc.value)


def test_gpu_type_filter_with_extra_fields(gpu_api):
    """测试额外字段透传"""
    mock_resp = {"code": 10000, "message": "ok", "data": {"brand": "AMD"}}
    payload = {"region": "us", "gpuBrand": "AMD", "memory": "16GB"}
    with patch.object(gpu_api, "http_post", return_value=mock_resp) as mock_post:
        resp = gpu_api.get_gpus_filter(payload)
        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        assert called_args[0] == "/api/resource/gpu/type/filter"
        assert called_kwargs["payload"]["memory"] == "16GB"
        assert resp["data"]["brand"] == "AMD"
