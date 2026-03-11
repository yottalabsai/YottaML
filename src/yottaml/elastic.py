from typing import List, Optional, Union, Any
from yottaml import API  # noqa: F401
from yottaml.lib.enums import ElasticDeploymentStatusEnum
from yottaml.lib.utils import (
    check_required_parameter,
    check_required_parameters,
    check_is_positive_int,
    clean_none_value,
    _UNSET,
)

class ElasticApi(API):
    """
    Python client for Serverless (Elastic) OpenAPI v2 endpoints.

      - GET    /v2/serverless
      - GET    /v2/serverless/{id}
      - POST   /v2/serverless
      - PATCH  /v2/serverless/{id}
      - POST   /v2/serverless/{id}/stop
      - POST   /v2/serverless/{id}/start
      - DELETE /v2/serverless/{id}
      - PUT    /v2/serverless/{id}/workers?count=N
      - GET    /v2/serverless/{id}/workers
    """

    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    # ------------------------- Create deployment -------------------------
    def create_deployment(
        self,
        name: str,
        image: str,
        resources: List[dict],
        workers: int,
        service_mode: str,
        container_volume_in_gb: int,
        image_registry: Optional[str] = None,
        credential_id: Optional[Union[int, str]] = None,
        min_single_card_vram_in_gb: Optional[int] = None,
        min_single_card_vcpu: Optional[int] = None,
        min_single_card_ram_in_gb: Optional[int] = None,
        initialization_command: Optional[str] = None,
        environment_vars: Optional[List[dict]] = None,
        expose: Optional[dict] = None,
        webhook: Optional[str] = None,
    ):
        """
        Create Serverless Endpoint.

        POST /v2/serverless

        Args:
            name (str): Endpoint name (max 20 chars).
            image (str): Container image.
            resources (List[dict]): Resource list, each with region/gpuType/gpuCount.
            workers (int): Initial workers count (must be positive).
            service_mode (str): ALB, QUEUE, or CUSTOM.
            container_volume_in_gb (int): Container volume size in GB (min 20).
            image_registry (str, optional): Image registry URL.
            credential_id (int|str, optional): Container registry credential ID.
            min_single_card_vram_in_gb (int, optional): Minimum single-card VRAM in GB.
            min_single_card_vcpu (int, optional): Minimum single-card vCPU count.
            min_single_card_ram_in_gb (int, optional): Minimum single-card RAM in GB.
            initialization_command (str, optional): Container initialization command.
            environment_vars (List[dict], optional): Environment variables list.
            expose (dict, optional): Exposed port configuration.
            webhook (str, optional): Webhook URL for worker status notifications.
        """
        check_required_parameters(
            [
                [name, "name"],
                [image, "image"],
                [resources, "resources"],
                [workers, "workers"],
                [service_mode, "service_mode"],
                [container_volume_in_gb, "container_volume_in_gb"],
            ]
        )

        if not isinstance(workers, int) or workers <= 0:
            raise ValueError("workers must be a positive integer")

        payload = clean_none_value(
            {
                "name": name,
                "image": image,
                "imageRegistry": image_registry,
                "containerRegistryAuthId": credential_id,
                "resources": resources,
                "minSingleCardVramInGb": min_single_card_vram_in_gb,
                "minSingleCardVcpu": min_single_card_vcpu,
                "minSingleCardRamInGb": min_single_card_ram_in_gb,
                "workers": workers,
                "serviceMode": service_mode,
                "containerVolumeInGb": container_volume_in_gb,
                "initializationCommand": initialization_command,
                "environmentVars": environment_vars,
                "expose": expose,
                "webhook": webhook,
            }
        )

        return self.http_post("/v2/serverless", payload=payload)

    # ------------------------- List deployments -------------------------
    def get_deployments(self, status_list: Optional[List[Union[str, ElasticDeploymentStatusEnum]]] = None, **kwargs):
        """
        Get Serverless Endpoint list.

        GET /v2/serverless

        Args:
            status_list (List[str], optional): Filter by status names.
            **kwargs: Additional query params (pass-through).

        Returns:
            Json: List of serverless endpoint details.
        """
        payload = {**kwargs}

        if status_list:
            normalized: List[str] = []
            for s in status_list:
                if s is None:
                    continue
                v = s.value if isinstance(s, ElasticDeploymentStatusEnum) else str(s)
                v = v.strip().upper()
                if v:
                    normalized.append(v)
            if normalized:
                payload["statusList"] = ",".join(normalized)

        return self.http_get("/v2/serverless", payload=payload)

    # ------------------------- Get one deployment -------------------------
    def get_deployment_detail(self, deployment_id: Union[int, str]):
        """
        Get Serverless Endpoint detail by ID.

        GET /v2/serverless/{id}

        Args:
            deployment_id (int|str): Deployment ID (positive integer).

        Returns:
            Json: Deployment detail payload.
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        return self.http_get(f"/v2/serverless/{int(deployment_id)}")

    # ------------------------- Scale workers -------------------------
    def scale_workers(self, deployment_id: Union[int, str], workers: int):
        """
        Scale Serverless Endpoint workers.

        PUT /v2/serverless/{id}/workers?count=N

        Args:
            deployment_id (int|str): Deployment ID (positive integer).
            workers (int): Target worker count (>= 0).

        Returns:
            Json: Standard success response.
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")
        if not isinstance(workers, int) or workers < 0:
            raise ValueError("workers must be a non-negative integer")

        return self.http_put(
            f"/v2/serverless/{int(deployment_id)}/workers",
            payload={"count": workers},
        )

    # ------------------------- Update deployment -------------------------
    def update_deployment(
        self,
        deployment_id: Union[int, str],
        name: str,
        resources: List[dict],
        workers: int,
        container_volume_in_gb: int,
        credential_id: Any = _UNSET,
        min_single_card_vram_in_gb: Any = _UNSET,
        min_single_card_vcpu: Any = _UNSET,
        min_single_card_ram_in_gb: Any = _UNSET,
        initialization_command: Any = _UNSET,
        environment_vars: Any = _UNSET,
        expose: Any = _UNSET,
        webhook: Any = _UNSET,
    ):
        """
        Update Serverless Endpoint.

        PATCH /v2/serverless/{id}

        Args:
            deployment_id (int|str): Deployment ID.
            name (str): Endpoint name.
            resources (List[dict]): Resource list, each with region/gpuType/gpuCount.
            workers (int): Target workers count (must be positive).
            container_volume_in_gb (int): Container volume size in GB.
            credential_id (int|str, optional): Container registry credential ID.
            min_single_card_vram_in_gb (int, optional): Minimum single-card VRAM in GB.
            min_single_card_vcpu (int, optional): Minimum single-card vCPU count.
            min_single_card_ram_in_gb (int, optional): Minimum single-card RAM in GB.
            initialization_command (str, optional): Container initialization command.
            environment_vars (List[dict], optional): Environment variables list.
            expose (dict, optional): Exposed port configuration.
            webhook (str, optional): Webhook URL for worker status notifications.
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")
        check_required_parameters(
            [
                [name, "name"],
                [resources, "resources"],
                [workers, "workers"],
                [container_volume_in_gb, "container_volume_in_gb"],
            ]
        )

        if not isinstance(workers, int) or workers <= 0:
            raise ValueError("workers must be a positive integer")

        payload = {
            "name": name,
            "resources": resources,
            "workers": workers,
            "containerVolumeInGb": container_volume_in_gb,
        }

        if credential_id is not _UNSET:
            payload["credentialId"] = credential_id
        if min_single_card_vram_in_gb is not _UNSET:
            payload["minSingleCardVramInGb"] = min_single_card_vram_in_gb
        if min_single_card_vcpu is not _UNSET:
            payload["minSingleCardVcpu"] = min_single_card_vcpu
        if min_single_card_ram_in_gb is not _UNSET:
            payload["minSingleCardRamInGb"] = min_single_card_ram_in_gb
        if initialization_command is not _UNSET:
            payload["initializationCommand"] = initialization_command
        if environment_vars is not _UNSET:
            payload["environmentVars"] = environment_vars
        if expose is not _UNSET:
            payload["expose"] = expose
        if webhook is not _UNSET:
            payload["webhook"] = webhook

        return self.http_patch(f"/v2/serverless/{int(deployment_id)}", payload=payload)

    # ------------------------- Control deployment lifecycle -------------------------
    def stop_deployment(self, deployment_id: Union[int, str]):
        """Stop a specific Serverless Endpoint.

        POST /v2/serverless/{id}/stop
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        return self.http_post(f"/v2/serverless/{int(deployment_id)}/stop", payload=None)

    def start_deployment(self, deployment_id: Union[int, str]):
        """Start or resume a specific Serverless Endpoint.

        POST /v2/serverless/{id}/start
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        return self.http_post(f"/v2/serverless/{int(deployment_id)}/start", payload=None)

    def delete_deployment(self, deployment_id: Union[int, str]):
        """Delete a specific Serverless Endpoint.

        DELETE /v2/serverless/{id}
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        return self.http_delete(f"/v2/serverless/{int(deployment_id)}", payload=None)

    # ------------------------- List workers for deployment -------------------------
    def get_workers(
        self,
        deployment_id: Union[int, str],
        status_list: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Get all workers of a specific Serverless Endpoint.

        GET /v2/serverless/{id}/workers
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        payload = {**kwargs}
        if status_list:
            payload["statusList"] = ",".join([str(s).strip().upper() for s in status_list if str(s).strip()])

        return self.http_get(f"/v2/serverless/{int(deployment_id)}/workers", payload=payload)
