import soxr
import numpy as np

class AudioPreprocess: 
    """
    Streaming audio preprocessing
    """
    def __init__(
        self,
        input_rate: int = 48000,
        input_channels: int = 2,
        output_rate: int = 16000,
        chunk_duration_ms: int = 32
    ):
        self.input_rate = input_rate
        self.input_channels = input_channels
        self.output_rate = output_rate
        self.chunk_duration_ms = chunk_duration_ms

        self.resampler = soxr.ResampleStream(
            in_rate=self.input_rate,    
            out_rate=self.output_rate,
            num_channels=1,
            dtype="float32",
            quality="HQ"
        )
        self._pending = np.empty(0, dtype=np.float32)


    def process_mono(self, stream_buffer):
        audio_array = np.frombuffer(
            stream_buffer,
            dtype=np.int16
        )

        if len(audio_array) % self.input_channels != 0:
            raise ValueError("Invalid audio buffer size")

        # Stereo -> Mono
        audio_stereo = audio_array.reshape(
            -1, self.input_channels
        )

        audio_mono = audio_stereo.astype(
            np.float32
        ).mean(axis=1)


        # normalize to [-1, +1]
        audio_mono /= 32768.0

        audio_resampled = self.resampler.resample_chunk(
            audio_mono,
            last=False
        )

        return audio_resampled



    def chunk_sample(self, audio_mono):
        """Return complete fixed-size output chunks and retain the remainder."""
        chunk_size = int(self.output_rate * self.chunk_duration_ms / 1000)
        self._pending = np.concatenate(
            (self._pending, np.asarray(audio_mono, dtype=np.float32))
        )

        chunk_count = len(self._pending) // chunk_size
        if chunk_count == 0:
            return []

        end = chunk_count * chunk_size
        chunks = [
            self._pending[start:start + chunk_size].copy()
            for start in range(0, end, chunk_size)
        ]
        self._pending = self._pending[end:]
        return chunks





        