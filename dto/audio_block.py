from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class AudioBlock:
    sequence: int
    timestamp: float

    sample_rate: int
    channels: int
    sample_format: Literal["int16"]

    frames_per_channel: int
    data: bytes

    @property
    def duration(self) -> float:
        return self.frames_per_channel / self.sample_rate

    @property
    def start_sample(self) -> int:
        return (self.sequence - 1) * self.frames_per_channel

    @property
    def end_sample(self) -> int:
        return self.start_sample + self.frames_per_channel