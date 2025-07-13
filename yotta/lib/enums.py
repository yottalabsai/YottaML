from enum import Enum


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
