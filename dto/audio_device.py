from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum): 
    MICROPHONE = "microphone"
    LOOPBACK = "loopback"

@dataclass
class AudioDevice: 
    index: int
    name: str
    device_type: DeviceType
    host_api: str

    sample_rate: int
    channels: int

    sample_width: int = 2

    @property
    def is_stereo(self) -> bool:
        return self.channels >= 2
