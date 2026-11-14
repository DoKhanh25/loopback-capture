from dataclasses import dataclass


@dataclass
class AudioConfig: 
    input_rate: int = 48000
    input_channel: int = 2 
    output_rate: int = 16000
    chunk_duration_ms: int = 32
    frames_per_buffer: int = 1024
