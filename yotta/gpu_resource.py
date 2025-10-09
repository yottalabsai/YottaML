from typing import List, Optional
from yotta import API
from yotta.lib.utils import check_required_parameter


class GpuResourceApi(API):
    """GPU Resource API SDK for YottaLabs"""

    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def get_gpus(self, search_request: dict):
        """
        Get GPU resource list
        POST /api/resource/gpu/list

        Args:
            search_request (dict): payload containing filters, pagination, etc.
        Returns:
            Json: List of GpuResourceDetailResponse
        """
        check_required_parameter(search_request, "search_request")
        return self.http_post("/api/resource/gpu/list", payload=search_request)

    def get_gpus_filter(self, search_request: dict):
        """
        Get GPU type filter
        POST /api/resource/gpu/type/filter

        Args:
            search_request (dict): filter criteria for GPU types
        Returns:
            Json: GpuResourceDetailResponse
        """
        check_required_parameter(search_request, "search_request")
        return self.http_post("/api/resource/gpu/type/filter", payload=search_request)
