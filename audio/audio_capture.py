from collections.abc import Iterator
from threading import Event

import pyaudiowpatch as pyaudio
from pyaudiowpatch import PyAudio, Stream

from audio.device_manager import DeviceManager
from dto.audio_device import DeviceType


class AudioCapture:

    def __init__(
        self,
        audio: PyAudio,
        device_manager: DeviceManager,
    ):
        self.audio = audio
        self.device_manager = device_manager

        self._streams: dict[DeviceType, Stream] = {}

    def capture(
        self,
        *,
        loopback: bool = True,
        sample_rate: int = 16000,
        channels: int = 2,
        frames_per_buffer: int = 1024,
    ) -> Iterator[bytes]:

        if not loopback:
            raise ValueError("Loopback capture is required")

        if DeviceType.LOOPBACK in self._streams:
            raise RuntimeError("Loopback stream is already open")

        device = self.device_manager.get_default_loopback()

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device.index,
            frames_per_buffer=frames_per_buffer,
        )

        self._streams[DeviceType.LOOPBACK] = stream

        try:
            while True:

                audio_chunk = stream.read(
                    num_frames=frames_per_buffer,
                    exception_on_overflow=False,
                )

                yield audio_chunk

        finally:
            self._streams.pop(DeviceType.LOOPBACK, None)
            self._close_stream(stream)



    @staticmethod
    def _close_stream(stream: Stream) -> None:
        if stream.is_active():
            stream.stop_stream()

        stream.close()
