import numpy as np
import torch
from silero_vad import VADIterator, load_silero_vad


class VadProcess:
    """
    Stateful streaming voice-activity detection over fixed-size mono chunks.

    Feed every chunk produced by AudioPreprocess.chunk_sample() in order.
    This class is pure logic: no threads, no queues.
    """

    def __init__(
        self,
        *,
        model=None,
        sampling_rate: int = 16000,
        threshold: float = 0.5,
        min_silence_duration_ms: int = 400,
        speech_pad_ms: int = 100,
    ):
        if sampling_rate not in (8000, 16000):
            raise ValueError("sampling_rate must be 8000 or 16000")

        self.sampling_rate = sampling_rate
        self._window_samples = 512 if sampling_rate == 16000 else 256

        self._iterator = VADIterator(
            load_silero_vad() if model is None else model,
            sampling_rate=self.sampling_rate,
            threshold=threshold,
            min_silence_duration_ms=min_silence_duration_ms,
            speech_pad_ms=speech_pad_ms,
        )
        self._speech_chunks: list[np.ndarray] = []
        self._in_speech = False

    @property
    def in_speech(self) -> bool:
        return self._in_speech

    def process(self, chunk: np.ndarray) -> np.ndarray | None:
        """
        Consume one chunk.

        Returns the complete mono utterance when the VAD reports the end of
        speech, otherwise None. The returned audio includes every chunk from
        the "start" event through the "end" event.
        """
        samples = self._validate(chunk)

        event = self._iterator(torch.from_numpy(samples))

        if event is not None and "start" in event:
            self._speech_chunks = [samples]
            self._in_speech = True
            return None

        if self._in_speech:
            self._speech_chunks.append(samples)

        if event is not None and "end" in event and self._in_speech:
            segment = np.concatenate(self._speech_chunks)
            self._speech_chunks = []
            self._in_speech = False
            return segment

        return None

    def flush(self) -> np.ndarray | None:
        """
        Return the in-progress utterance (e.g. on shutdown) and reset state.

        Returns None when no speech is pending.
        """
        if not self._in_speech or not self._speech_chunks:
            self.reset()
            return None

        segment = np.concatenate(self._speech_chunks)
        self.reset()
        return segment

    def reset(self) -> None:
        """Reset both the VAD model state and any buffered speech."""
        self._iterator.reset_states()
        self._speech_chunks = []
        self._in_speech = False

    def _validate(self, chunk: np.ndarray) -> np.ndarray:
        samples = np.ascontiguousarray(chunk, dtype=np.float32)

        if samples.ndim != 1:
            raise ValueError(f"Expected a mono 1-D chunk, got shape {samples.shape}")

        if samples.size != self._window_samples:
            raise ValueError(
                f"Expected {self._window_samples} samples per chunk at "
                f"{self.sampling_rate} Hz, got {samples.size}. Keep "
                "AudioConfig.chunk_duration_ms aligned with output_rate."
            )

        return samples
