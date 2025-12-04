from enum import Enum
from typing import List
from enum import IntEnum


class ResourceType(Enum):
    CPU = "CPU"
    GPU = "GPU"


class GPUType(Enum):
    NVIDIA_GeForce_RTX_4090_24G = "NVIDIA_GeForce_RTX_4090_24G"
    NVIDIA_GeForce_RTX_5090_32G = "NVIDIA_GeForce_RTX_5090_32G"
    NVIDIA_H100_80GB_HBM3_80G = "NVIDIA_H100_80GB_HBM3_80G"
    NVIDIA_L4_24G = "NVIDIA_L4_24G"


class CloudType(Enum):
    SECURE = "SECURE"
    COMMUNITY = "COMMUNITY"


class OfficialImageType(Enum):
    OFFICIAL = "OFFICIAL"
    CUSTOM = "CUSTOM"


class ImagePublicType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class PodStatus(Enum):
    INITIALIZE = "INITIALIZE"
    RUNNING = "RUNNING"
    PAUSING = "PAUSING"
    PAUSED = "PAUSED"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"


class ElasticDeploymentStatusEnum(str, Enum):
    INITIALIZING = "INITIALIZING"  # 0
    RUNNING = "RUNNING"  # 1
    STOPPING = "STOPPING"  # 2
    STOPPED = "STOPPED"  # 3
    FAILED = "FAILED"  # 4

    @classmethod
    def list(cls) -> List[str]:
        return [e.value for e in cls]

    @classmethod
    def active(cls) -> List[str]:
        return [cls.INITIALIZING.value, cls.RUNNING.value]


class TaskStatus(IntEnum):
    """
    Task.status (backend semantics)
      0 = PROCESSING
      1 = DELIVERED
      2 = SUCCESS
      3 = FAILED
    """
    PROCESSING = 0
    DELIVERED = 1
    SUCCESS = 2
    FAILED = 3


class ResultSendStatus(IntEnum):
    """
    Task.resultSendStatus (backend semantics)
      0 = INIT
      1 = SUCCESS
      2 = FAILED
      3 = MAX_RETRIES_EXCEEDED
    """
    INIT = 0
    SUCCESS = 1
    FAILED = 2
    MAX_RETRIES_EXCEEDED = 3
