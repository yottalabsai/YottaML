from typing import List, Optional

from yotta import API
from yotta.lib.enums import ResourceType
from yotta.lib.utils import check_is_positive_int, none_to_zero, check_gpu_count, clean_none_value
from yotta.lib.utils import check_required_parameter
from yotta.lib.utils import check_required_parameters


class PodApi(API):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def get_pods(self, region_list: list[str] = None, status_list: list[int] = None, **kwargs):
        """Get Pod list

        GET /openapi/v1/pods/list

        Args:
            region_list (list[str], optional): Filter pods by region, e.g. ["sg", "us-east-1"].
            status_list (list[int], optional): Filter pods by status. Available values:
                - 0 INITIALIZE
                - 1 RUNNING
                - 2 PAUSING
                - 3 PAUSED
                - 4 TERMINATING
                - 6 FAILED
        **kwargs: Additional query parameters, will be passed directly into query string.

        Returns:
            Json: List of pod details ordered by updatedAt (descending).

        """
        payload = {**kwargs}

        if region_list:
            payload["regionList"] = ",".join(region_list)

        if status_list:
            payload["statusList"] = ",".join(map(str, status_list))

        url_path = "/openapi/v1/pods/list"
        return self.http_get(url_path, payload=payload)

    def delete_pod(self, pod_id: str):
        """Delete Pod

        DELETE /openapi/v1/pods/{pod_id}

        Args:
            pod_id (str): ID of the pod to delete. Must be a positive integer.

        Returns:
            Json: Response indicating success of deletion

        Raises:
            ValueError: If pod_id is not a valid positive integer
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        url_path = f"/openapi/v1/pods/{pod_id}"
        return self.http_delete(url_path, payload=None)

    def new_pod(
            self,
            image: str,
            gpu_type: str,
            region: Optional[str] = None,
            cloud_type: Optional[str] = None,
            pod_name: Optional[str] = None,
            official_image: Optional[str] = None,
            image_public_type: Optional[str] = None,
            image_registry_username: Optional[str] = None,
            image_registry_token: Optional[str] = None,
            resource_type: Optional[str] = None,
            gpu_count: Optional[int] = None,
            min_single_card_ram_in_gb: Optional[int] = None,
            container_volume_in_gb: Optional[int] = None,
            persistent_volume_in_gb: Optional[int] = None,
            persistent_mount_path: Optional[str] = None,
            initialization_command: Optional[str] = None,
            environment_vars: Optional[List[dict]] = None,
            expose: Optional[List[dict]] = None,
    ):
        """Create a new pod

        POST /openapi/v1/pods

        Args:
            image (str): Image name
            gpu_type (str, optional): gpu type
            region (str, optional): Region
            cloud_type (str, optional): CloudTypeEnum SECURE, COMMUNITY. Defaults to "SECURE"
            pod_name (str): Pod nickname. Defaults to "My Pod"
            official_image (str, optional): ImageSourceEnum OFFICIAL, CUSTOM. Defaults to "CUSTOM"
            image_public_type (str, optional): ImagePublicTypeEnum PUBLIC, PRIVATE. Defaults to "PUBLIC"
            image_registry_username (str, optional): Image registry username
            image_registry_token (str, optional): Image registry token
            resource_type (str, optional): ResourceType GPU, CPU. Defaults to "GPU"
            gpu_count (int): Number of GPUs to allocate. Required if resource_type is "GPU". Min 1
            min_single_card_ram_in_gb (int, optional): Minimum single GPU RAM unit: GB. Depends on gpu_type.
            container_volume_in_gb (int, optional): Container volume unit:GB. Depends on gpu_type
            persistent_volume_in_gb (int, optional): Persistent volume unit:GB. Depends on gpu_type
            persistent_mount_path (str, optional): Persistent mount path
            initialization_command (str, optional): Initialization command
            environment_vars (List[dict], optional): Image needed environment vars [{"key":"myKey", "value": myValue}]
            expose (List[dict], optional): Expose ports [{"port": 8000, "protocol": "HTTP"}]

        Returns:
            Json: Response containing the created pod ID
        """
        # Required parameters validation
        check_required_parameters([
            [image, "image"],
            [gpu_type, "gpu_type"],
        ])

        if resource_type is None or resource_type == ResourceType.GPU.value:
            check_required_parameter(gpu_count, "gpu_count")
            check_gpu_count(gpu_count)

        if none_to_zero(persistent_volume_in_gb, "persistent_volume_in_gb") > 0:
            check_required_parameter(persistent_mount_path, "persistent_mount_path")

        # Create the request object
        payload = clean_none_value({
            "region": region,
            "cloudType": cloud_type,
            "podName": pod_name,
            "image": image,
            "officialImage": official_image,
            "imagePublicType": image_public_type,
            "imageRegistryUsername": image_registry_username,
            "imageRegistryToken": image_registry_token,
            "resourceType": resource_type,
            "gpuType": gpu_type,
            "gpuCount": gpu_count,
            "minSingleCardRamInGb": min_single_card_ram_in_gb,
            "containerVolumeInGb": container_volume_in_gb,
            "persistentVolumeInGb": persistent_volume_in_gb,
            "persistentMountPath": persistent_mount_path,
            "initializationCommand": initialization_command,
            "environmentVars": environment_vars,
            "expose": expose
        })

        url_path = "/openapi/v1/pods/create"
        return self.http_post(url_path, payload)

    def pause_pod(self, pod_id: str):
        """Pause Pod

        POST /openapi/v1/pods/pause/{pod_id}

        Args:
            pod_id (str): ID of the pod to pause. Must be a positive integer.

        Returns:
            Json: Response indicating success of pause operation

        Raises:
            ValueError: If pod_id is not a valid positive integer
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        url_path = f"/openapi/v1/pods/pause/{pod_id}"
        return self.http_post(url_path, payload=None)

    def resume_pod(self, pod_id: str):
        """Resume Pod

        POST /openapi/v1/pods/resume/{pod_id}

        Args:
            pod_id (str): ID of the pod to resume. Must be a positive integer.

        Returns:
            Json: Response indicating success of resume operation

        Raises:
            ValueError: If pod_id is not a valid positive integer
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        url_path = f"/openapi/v1/pods/resume/{pod_id}"
        return self.http_post(url_path, payload=None)

    def get_pod(self, pod_id: str, **kwargs):
        """Get pod detail by ID

        GET /openapi/v1/pods/{pod_id}

        Args:
            pod_id (str): ID of the pod to retrieve detail. Must be a positive integer.

        Returns:
            Json: Pod detail payload

        Raises:
            ValueError: If pod_id is not a positive integer.
        """
        check_required_parameter(pod_id, "pod_id")
        check_is_positive_int(pod_id, "pod_id")

        # Compose query payload (allow extra query params to pass-through)
        payload = {"id": pod_id, **kwargs}

        url_path = f"/openapi/v1/pods/{pod_id}"
        return self.http_get(url_path)