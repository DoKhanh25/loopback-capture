from dataclasses import dataclass
import numpy as np

@dataclass
class AudioFrame: 
    sequence_id: int
    timestamp: float
    sample_rate: int
    samples: np.ndarray