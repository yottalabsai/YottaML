from yottaml import API


class GpuApi(API):
    """GPU/VM Types API SDK for YottaLabs"""

    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def get_gpus(self):
        """
        Get available GPU types and their region availability.

        GET /v2/vms/types

        Returns:
            Json: List of GPU types with region availability and vmTypeId.
        """
        return self.http_get("/v2/vms/types")
