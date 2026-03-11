from enum import Enum
from typing import List


class ResourceType(Enum):
    CPU = "CPU"
    GPU = "GPU"


class GPUType(Enum):
    NVIDIA_RTX_4090_24G = "NVIDIA_RTX_4090_24G"
    NVIDIA_RTX_5090_32G = "NVIDIA_RTX_5090_32G"
    NVIDIA_H100_80G     = "NVIDIA_H100_80G"
    NVIDIA_A100_PCIE_80G = "NVIDIA_A100_PCIe_80G"


class ImagePublicType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class PodStatus(Enum):
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    TERMINATED = "TERMINATED"


class ElasticDeploymentStatusEnum(str, Enum):
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"

    @classmethod
    def list(cls) -> List[str]:
        return [e.value for e in cls]

    @classmethod
    def active(cls) -> List[str]:
        return [cls.INITIALIZING.value, cls.RUNNING.value]


class TaskStatus(str, Enum):
    PROCESSING = "PROCESSING"
    DELIVERED = "DELIVERED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ResultSendStatus(str, Enum):
    INIT = "INIT"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    MAX_RETRIES_EXCEEDED = "MAX_RETRIES_EXCEEDED"