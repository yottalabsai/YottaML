import pytest
from unittest.mock import patch
from yotta.gpu import GpuApi
from yotta.error import ClientError
from yotta.error import ParameterRequiredError


@pytest.fixture
def gpu_api():
    """创建一个 GpuResourceApi 实例"""
    return GpuApi(api_key="fake_api_key", base_url="https://api.test.yottalabs.ai")

def test_gpu_list_success(gpu_api):
    """测试 gpu_list 正常返回"""
    mock_response = {
        "code": 10000,
        "message": "success",
        "data": [{"gpuType": "NVIDIA_L4", "gpuCount": 24}]
    }
    payload = {"region": "us-east-1", "page": 1, "size": 10}

    with patch.object(gpu_api, "http_post", return_value=mock_response) as mock_post:
        resp = gpu_api.get_gpus(payload)
        assert resp == mock_response
        mock_post.assert_called_once_with("/openapi/v1/gpu/list", payload=payload)
        assert resp["data"][0]["gpuType"] == "NVIDIA_L4"


def test_gpu_list_multiple_pages(gpu_api):
    """测试分页逻辑传参"""
    payload = {"region": "sg", "page": 2, "size": 20}
    with patch.object(gpu_api, "http_post", return_value={"code": 10000, "data": []}) as mock_post:
        gpu_api.get_gpus(payload)
        called_path, called_kwargs = mock_post.call_args
        assert called_path[0].endswith("/gpu/list")
        assert called_kwargs["payload"]["page"] == 2
        assert called_kwargs["payload"]["size"] == 20


def test_gpu_list_invalid_param(gpu_api):
    """测试 search_request 缺失时抛出异常"""
    with pytest.raises(ParameterRequiredError):
        gpu_api.get_gpus(None)



def test_gpu_list_client_error(gpu_api):
    """测试 HTTP 客户端异常"""
    with patch.object(gpu_api, "http_post", side_effect=ClientError(400, 40001, "Bad Request", {}, None)):
        with pytest.raises(ClientError) as exc:
            gpu_api.get_gpus({"region": "us-east-1"})
        assert exc.value.status_code == 400
        assert exc.value.error_code == 40001


def test_gpu_list_unexpected_response_code(gpu_api):
    """测试非 10000 返回码逻辑"""
    mock_resp = {"code": 9999, "message": "internal error", "data": None}
    with patch.object(gpu_api, "http_post", return_value=mock_resp):
        resp = gpu_api.get_gpus({"region": "us-east-1"})
        assert resp["code"] != 10000
        assert "internal" in resp["message"].lower()
