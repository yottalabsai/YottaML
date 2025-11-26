from enum import Enum
from typing import List, Optional, Union
from yotta import API
from yotta.lib.enums import ElasticEndpointStatusEnum
from yotta.lib.utils import (
    check_required_parameter,
    check_required_parameters,
    check_is_positive_int,
    clean_none_value,
)

class ElasticApi(API):
    """
    Python client for Elastic Deployment OpenAPI endpoints.

      - GET  /openapi/v1/elastic/deploy/list
      - GET  /openapi/v1/elastic/deploy/{id}
      - POST /openapi/v1/elastic/deploy/{id}/workers
    """

    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    # ------------------------- Create deployment -------------------------
    def create_deployment(
        self,
        name: str,
        image: str,
        image_registry: str,
        resources: List[dict],
        workers: int,
        service_mode: str,
        credential_id: Union[int, str],
        min_single_card_vram_in_gb: Optional[int] = None,
        min_single_card_vcpu: Optional[int] = None,
        min_single_card_ram_in_gb: Optional[int] = None,
        container_volume_in_gb: Optional[int] = None,
        initialization_command: Optional[str] = None,
        environment_vars: Optional[List[dict]] = None,
        expose: Optional[List[dict]] = None,
    ):
        """
        Create Elastic Deployment.

        POST /openapi/v1/elastic/deploy/create

        Args:
            name (str): Deployment name.
            image (str): Container image.
            image_registry (str): Image registry URL, e.g. https://index.docker.io/v1.
            resources (List[dict]): Resource list, each with region/gpuType/gpuCount.
            workers (int): Initial workers count (must be positive).
            service_mode (str): Service mode, e.g. "ALB".
            credential_id (int|str): Credential ID used by this deployment.
            min_single_card_vram_in_gb (int, optional): Minimum single-card VRAM in GB.
            min_single_card_vcpu (int, optional): Minimum single-card vCPU count.
            min_single_card_ram_in_gb (int, optional): Minimum single-card RAM in GB.
            container_volume_in_gb (int, optional): Container volume size in GB.
            initialization_command (str, optional): Container initialization command.
            environment_vars (List[dict], optional): Environment variables list.
            expose (List[dict], optional): Exposed ports configuration.
        """
        check_required_parameters(
            [
                [name, "name"],
                [image, "image"],
                [image_registry, "image_registry"],
                [resources, "resources"],
                [workers, "workers"],
                [service_mode, "service_mode"],
                [credential_id, "credential_id"],
            ]
        )

        if not isinstance(workers, int) or workers <= 0:
            raise ValueError("workers must be a positive integer")

        # Validate credential_id is positive integer-like
        check_is_positive_int(credential_id, "credential_id")

        payload = clean_none_value(
            {
                "name": name,
                "image": image,
                "imageRegistry": image_registry,
                "resources": resources,
                "minSingleCardVramInGb": min_single_card_vram_in_gb,
                "minSingleCardVcpu": min_single_card_vcpu,
                "minSingleCardRamInGb": min_single_card_ram_in_gb,
                "workers": workers,
                "serviceMode": service_mode,
                "credentialId": credential_id,
                "containerVolumeInGb": container_volume_in_gb,
                "initializationCommand": initialization_command,
                "environmentVars": environment_vars,
                "expose": expose,
            }
        )

        url_path = "/openapi/v1/elastic/deploy/create"
        return self.http_post(url_path, payload=payload)

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
    def get_endpoint(self, deployment_id: Union[int, str]):
        """
        Get Elastic Deployment detail by ID.

        GET /openapi/v1/elastic/deploy/{id}

        Args:
            deployment_id (int|str): Deployment ID (positive integer).

        Returns:
            Json: Deployment detail payload.
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}"
        return self.http_get(url_path)

    # ------------------------- Scale workers -------------------------
    def scale_workers(self, deployment_id: Union[int, str], workers: int):
        """
        Scale Elastic Deployment workers.

        POST /openapi/v1/elastic/deploy/{id}/workers

        Args:
            deployment_id (int|str): Deployment ID (positive integer).
            workers (int): Target workers (>= 0).

        Returns:
            Json: Standard success response with data=None.
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")
        if not isinstance(workers, int) or workers < 0:
            raise ValueError("workers must be a non-negative integer")

        payload = clean_none_value(
            {
                "workers": workers
            }
        )

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}/workers"
        return self.http_post(url_path, payload=payload)

    # ------------------------- Update deployment -------------------------
    def update_deployment(
        self,
        deployment_id: Union[int, str],
        name: str,
        resources: List[dict],
        workers: int,
        min_single_card_vram_in_gb: Optional[int] = None,
        min_single_card_vcpu: Optional[int] = None,
        min_single_card_ram_in_gb: Optional[int] = None,
        container_volume_in_gb: Optional[int] = None,
        initialization_command: Optional[str] = None,
        environment_vars: Optional[List[dict]] = None,
        expose: Optional[List[dict]] = None,
    ):
        """
        Update Elastic Deployment.

        POST /openapi/v1/elastic/deploy/{id}/update
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")
        check_required_parameters(
            [
                [name, "name"],
                [resources, "resources"],
                [workers, "workers"],
            ]
        )

        if not isinstance(workers, int) or workers <= 0:
            raise ValueError("workers must be a positive integer")

        payload = clean_none_value(
            {
                "name": name,
                "resources": resources,
                "minSingleCardVramInGb": min_single_card_vram_in_gb,
                "minSingleCardVcpu": min_single_card_vcpu,
                "minSingleCardRamInGb": min_single_card_ram_in_gb,
                "workers": workers,
                "containerVolumeInGb": container_volume_in_gb,
                "initializationCommand": initialization_command,
                "environmentVars": environment_vars,
                "expose": expose,
            }
        )

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}/update"
        return self.http_post(url_path, payload=payload)

    # ------------------------- Control deployment lifecycle -------------------------
    def stop_deployment(self, deployment_id: Union[int, str]):
        """Stop a specific Elastic Deployment.

        POST /openapi/v1/elastic/deploy/{id}/stop
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}/stop"
        return self.http_post(url_path, payload=None)

    def run_deployment(self, deployment_id: Union[int, str]):
        """Run a specific Elastic Deployment.

        POST /openapi/v1/elastic/deploy/{id}/run
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}/run"
        return self.http_post(url_path, payload=None)

    def delete_deployment(self, deployment_id: Union[int, str]):
        """Delete a specific Elastic Deployment.

        DELETE /openapi/v1/elastic/deploy/{id}
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}"
        return self.http_delete(url_path, payload=None)

    # ------------------------- List workers for deployment -------------------------
    def get_workers(
        self,
        deployment_id: Union[int, str],
        status_list: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Get all workers of a specific Elastic Deployment.

        GET /openapi/v1/elastic/deploy/{id}/workers
        """
        check_required_parameter(deployment_id, "deployment_id")
        check_is_positive_int(deployment_id, "deployment_id")

        payload = {**kwargs}
        if status_list:
            payload["statusList"] = ",".join([str(s).strip().upper() for s in status_list if str(s).strip()])

        url_path = f"/openapi/v1/elastic/deploy/{int(deployment_id)}/workers"
        return self.http_get(url_path, payload=payload)
