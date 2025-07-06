from enum import Enum


class ResourceType(Enum):
    CPU = "CPU"
    GPU = "GPU"


class CloudType(Enum):
    SECURE = "SECURE"
    COMMUNITY = "COMMUNITY"


class OfficialImageType(Enum):
    OFFICIAL = "OFFICIAL"
    CUSTOM = "CUSTOM"


class ImagePublicType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE" 
