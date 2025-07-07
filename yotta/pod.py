from typing import List, Optional

from yotta import API
from yotta.lib.utils import check_required_parameter
from yotta.lib.utils import check_required_parameters


class PodApi(API):
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key, **kwargs)

    def get_pods(self, **kwargs):
        """All Pods

        GET /openapi/v1/pods/list

        Args:
        Returns:
            YottaResponse[List[PodDetail]]: List of pod details wrapped in API response
        """

        url_path = "/openapi/v1/pods/list"
        return self.http_get(url_path, payload=None)

    def delete_pod(self, pod_id: int):
        """Delete Pod

        DELETE /openapi/v1/pods/{pod_id}

        Args:
            pod_id (int): ID of the pod to delete

        Returns:
            YottaResponse[bool]: Response indicating success of deletion
        """
        check_required_parameter(pod_id, "pod_id")

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
            image (str): Docker image to use
            gpu_type (str, optional): Type of GPU to use (e.g., "A100", "V100"). Defaults to None
            region (str, optional): Region where the pod will be created. Defaults to "us-west-1"
            cloud_type (str, optional): Cloud type. Defaults to "SECURE"
            pod_name (str): Name of the pod
            official_image (str, optional): Whether the image is official. Defaults to "OFFICIAL"
            image_public_type (str, optional): Image visibility type. Defaults to "PUBLIC"
            image_registry_username (str, optional): Registry username for private images
            image_registry_token (str, optional): Registry token for private images
            resource_type (str, optional): Type of resource. Defaults to "GPU"
            gpu_count (int): Number of GPUs to allocate
            container_volume_in_gb (int, optional): Container volume size in GB. Defaults to 20
            persistent_volume_in_gb (int, optional): Persistent volume size in GB. Defaults to 10
            persistent_mount_path (str, optional): Mount path for persistent volume. Defaults to "/data"
            initialization_command (str, optional): Command to run during initialization. Defaults to ""
            environment_vars (List[dict], optional): List of environment variables. Each dict should have 'key' and 'value'
            expose (List[dict], optional): List of ports to expose. Each dict should have 'port' and 'protocol'

        Returns:
            YottaResponse[int]: Response containing the created pod ID
        """
        # Required parameters validation
        check_required_parameters([
            [image, "image"],
            [gpu_type, "gpu_type"],
        ])

        # Create the request object
        payload = {
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
            "containerVolumeInGb": container_volume_in_gb,
            "persistentVolumeInGb": persistent_volume_in_gb,
            "persistentMountPath": persistent_mount_path,
            "initializationCommand": initialization_command,
            "environmentVars": environment_vars,
            "expose": expose
        }

        url_path = "/openapi/v1/pods/create"
        return self.http_post(url_path, payload)
