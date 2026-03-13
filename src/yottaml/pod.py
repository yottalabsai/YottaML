from typing import List, Optional

from yottaml import API
from yottaml.lib.enums import ResourceType
from yottaml.lib.utils import check_is_positive_int, none_to_zero, check_gpu_count, clean_none_value
from yottaml.lib.utils import check_required_parameter
from yottaml.lib.utils import check_required_parameters


class PodApi(API):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def get_pods(self, region_list: list[str] = None, status_list: list[int] = None, **kwargs):
        """Get Pod list

        GET /v2/pods

        Args:
            region_list (list[str], optional): Filter pods by region, e.g. ["us-east-1"].
            status_list (list[int], optional): Filter pods by status codes.
            **kwargs: Additional query parameters, will be passed directly into query string.

        Returns:
            Json: List of pod details.
        """
        payload = {**kwargs}

        if region_list:
            payload["regionList"] = ",".join(region_list)

        if status_list:
            payload["statusList"] = ",".join(map(str, status_list))

        return self.http_get("/v2/pods", payload=payload)

    def delete_pod(self, pod_id: str):
        """Delete Pod

        DELETE /v2/pods/{id}

        Args:
            pod_id (str): ID of the pod to delete. Must be a positive integer.

        Returns:
            Json: Response indicating success of deletion

        Raises:
            ValueError: If pod_id is not a valid positive integer
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        return self.http_delete(f"/v2/pods/{pod_id}", payload=None)

    def new_pod(
            self,
            image: str,
            gpu_type: str,
            name: Optional[str] = None,
            regions: Optional[List[str]] = None,
            image_public_type: Optional[str] = None,
            image_registry: Optional[str] = None,
            image_registry_username: Optional[str] = None,
            image_registry_password: Optional[str] = None,
            container_registry_auth_id: Optional[int] = None,
            resource_type: Optional[str] = None,
            gpu_count: Optional[int] = None,
            min_single_card_vram_in_gb: Optional[int] = None,
            min_single_card_ram_in_gb: Optional[int] = None,
            min_single_card_vcpu: Optional[int] = None,
            shm_in_gb: Optional[int] = None,
            container_volume_in_gb: Optional[int] = None,
            persistent_volume_in_gb: Optional[int] = None,
            persistent_mount_path: Optional[str] = None,
            initialization_command: Optional[str] = None,
            environment_vars: Optional[List[dict]] = None,
            expose: Optional[List[dict]] = None,
            persistent_volumes: Optional[List[dict]] = None,
    ):
        """Create a new pod

        POST /v2/pods

        Args:
            image (str): Container image.
            gpu_type (str): GPU type, e.g. RTX_4090_24G.
            name (str, optional): Pod name.
            regions (list[str], optional): Acceptable region codes for scheduling.
            image_public_type (str, optional): PUBLIC or PRIVATE. Defaults to PUBLIC.
            image_registry (str, optional): Docker registry URL.
            image_registry_username (str, optional): Registry username (deprecated, use container_registry_auth_id).
            image_registry_password (str, optional): Registry password (deprecated, use container_registry_auth_id).
            container_registry_auth_id (int, optional): Stored credential ID for private images.
            resource_type (str, optional): GPU or CPU. Defaults to GPU.
            gpu_count (int): Number of GPUs. Must be power of 2.
            min_single_card_vram_in_gb (int, optional): Minimum single card VRAM in GB.
            min_single_card_ram_in_gb (int, optional): Minimum single card RAM in GB.
            min_single_card_vcpu (int, optional): Minimum single card vCPU count.
            shm_in_gb (int, optional): Shared memory size in GB.
            container_volume_in_gb (int, optional): Container volume in GB.
            persistent_volume_in_gb (int, optional): Persistent volume in GB.
            persistent_mount_path (str, optional): Persistent volume mount path.
            initialization_command (str, optional): Initialization command.
            environment_vars (list[dict], optional): Environment variables [{"key": "K", "value": "V"}].
            expose (list[dict], optional): Ports to expose [{"port": 8080, "protocol": "http"}].
            persistent_volumes (list[dict], optional): Persistent volumes configuration.

        Returns:
            Json: Response containing the created pod ID
        """
        check_required_parameters([
            [image, "image"],
            [gpu_type, "gpu_type"],
        ])

        if resource_type is None or resource_type == ResourceType.GPU.value:
            check_required_parameter(gpu_count, "gpu_count")
            check_gpu_count(gpu_count)

        if none_to_zero(persistent_volume_in_gb, "persistent_volume_in_gb") > 0:
            check_required_parameter(persistent_mount_path, "persistent_mount_path")

        payload = clean_none_value({
            "name": name,
            "regions": regions,
            "image": image,
            "imageRegistry": image_registry,
            "imagePublicType": image_public_type,
            "imageRegistryUsername": image_registry_username,
            "imageRegistryPassword": image_registry_password,
            "containerRegistryAuthId": container_registry_auth_id,
            "resourceType": resource_type,
            "gpuType": gpu_type,
            "gpuCount": gpu_count,
            "minSingleCardVramInGb": min_single_card_vram_in_gb,
            "minSingleCardRamInGb": min_single_card_ram_in_gb,
            "minSingleCardVcpu": min_single_card_vcpu,
            "shmInGb": shm_in_gb,
            "containerVolumeInGb": container_volume_in_gb,
            "persistentVolumeInGb": persistent_volume_in_gb,
            "persistentMountPath": persistent_mount_path,
            "initializationCommand": initialization_command,
            "environmentVars": environment_vars,
            "expose": expose,
            "persistentVolumes": persistent_volumes,
        })

        return self.http_post("/v2/pods", payload)

    def pause_pod(self, pod_id: str):
        """Pause Pod

        POST /v2/pods/{id}/pause

        Args:
            pod_id (str): ID of the pod to pause. Must be a positive integer.

        Returns:
            Json: Response indicating success of pause operation

        Raises:
            ValueError: If pod_id is not a valid positive integer
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        return self.http_post(f"/v2/pods/{pod_id}/pause", payload=None)

    def resume_pod(self, pod_id: str):
        """Resume Pod

        POST /v2/pods/{id}/resume

        Args:
            pod_id (str): ID of the pod to resume. Must be a positive integer.

        Returns:
            Json: Response indicating success of resume operation

        Raises:
            ValueError: If pod_id is not a valid positive integer
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        return self.http_post(f"/v2/pods/{pod_id}/resume", payload=None)

    def get_pod(self, pod_id: str, **kwargs):
        """Get pod detail by ID

        GET /v2/pods/{id}

        Args:
            pod_id (str): ID of the pod to retrieve detail. Must be a positive integer.

        Returns:
            Json: Pod detail payload

        Raises:
            ValueError: If pod_id is not a positive integer.
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        return self.http_get(f"/v2/pods/{pod_id}")
