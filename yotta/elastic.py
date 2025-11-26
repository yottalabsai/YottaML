from enum import Enum
from typing import List, Optional, Union
from yotta import API
from yotta.lib.utils import check_required_parameter, check_is_positive_int, clean_none_value

class ElasticEndpointStatusEnum(str, Enum):
    """Same semantics as backend Java enum."""
    INITIALIZING = "INITIALIZING"   # 0
    RUNNING = "RUNNING"             # 1
    STOPPING = "STOPPING"           # 2
    STOPPED = "STOPPED"             # 3
    FAILED = "FAILED"               # 4

    @classmethod
    def list(cls) -> List[str]:
        return [e.value for e in cls]

    @classmethod
    def active(cls) -> List[str]:
        return [cls.INITIALIZING.value, cls.RUNNING.value]

class ElasticApi(API):
    """
    Python client for Elastic Deployment OpenAPI endpoints.

    Mirrors Java controller:
      - GET  /openapi/v1/elastic/deploy/list
      - GET  /openapi/v1/elastic/deploy/{id}
      - POST /openapi/v1/elastic/deploy/{id}/workers
    """

    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    # ------------------------- List deployments -------------------------
    def get_endpoints(self, status_list: Optional[List[Union[str, ElasticEndpointStatusEnum]]] = None, **kwargs):
        """
        Get Elastic Deployment list.

        GET /openapi/v1/elastic/deploy/list

        Args:
            status_list (List[str], optional): Filter by status names. Example:
                ["INITIALIZING", "RUNNING"]. Values are case-insensitive.
            **kwargs: Additional query params (pass-through).

        Returns:
            Json: List of elastic deployment details.
        """
        payload = {**kwargs}

        # Java controller accepts List<String> statusList.
        if status_list:
            normalized: List[str] = []
            for s in status_list:
                if s is None:
                    continue
                v = s.value if isinstance(s, ElasticEndpointStatusEnum) else str(s)
                v = v.strip().upper()
                if v:
                    normalized.append(v)
            if normalized:
                payload["statusList"] = ",".join(normalized)

        url_path = "/openapi/v1/elastic/deploy/list"
        return self.http_get(url_path, payload=payload)

    # ------------------------- Get one deployment -------------------------
    def get_endpoint(self, endpoint_id: Union[int, str]):
        """
        Get Elastic Deployment detail by ID.

        GET /openapi/v1/elastic/deploy/{id}

        Args:
            endpoint_id (int|str): Deployment ID (positive integer).

        Returns:
            Json: Deployment detail payload.
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")

        url_path = f"/openapi/v1/elastic/deploy/{int(endpoint_id)}"
        return self.http_get(url_path)

    # ------------------------- Scale workers -------------------------
    def scale_workers(self, endpoint_id: Union[int, str], workers: int):
        """
        Scale Elastic Deployment workers.

        POST /openapi/v1/elastic/deploy/{id}/workers

        Args:
            endpoint_id (int|str): Deployment ID (positive integer).
            workers (int): Target workers (>= 0).

        Returns:
            Json: Standard success response with data=None.
        """
        check_required_parameter(endpoint_id, "endpoint_id")
        check_is_positive_int(endpoint_id, "endpoint_id")
        if not isinstance(workers, int) or workers < 0:
            raise ValueError("workers must be a non-negative integer")

        payload = clean_none_value({
            "workers": workers
        })

        url_path = f"/openapi/v1/elastic/deploy/{int(endpoint_id)}/workers"
        return self.http_post(url_path, payload=payload)
