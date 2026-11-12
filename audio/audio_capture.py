from collections.abc import Iterator

from pyaudiowpatch import PyAudio, Stream
import pyaudiowpatch as pyaudio

from audio.device_manager import DeviceManager
from dto.audio_device import AudioDevice, DeviceType


class AudioCapture:

    def __init__(self, audio: PyAudio, device_manager: DeviceManager):
        self.audio = audio
        self.device_manager = device_manager
        self._streams: dict[DeviceType, Stream] = {}

    def open_streams(
        self,
        *,
        microphone: bool = False,
        loopback: bool = False,
        frames_per_buffer: int = 1024,
    ) -> None:
        if not microphone and not loopback:

            raise ValueError("At least one capture source must be enabled")
        
        if self._streams:

            raise RuntimeError("Capture streams are already open")
        
        if frames_per_buffer <= 0:
            raise ValueError("frames_per_buffer must be positive")

        devices: list[AudioDevice] = []

        if microphone:
            devices.append(self.device_manager.get_default_microphone())

        if loopback:
            devices.append(self.device_manager.get_default_loopback())

        opened: dict[DeviceType, Stream] = {}
        try:
            for device in devices:
                opened[device.device_type] = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=device.channels,
                    rate=device.sample_rate,
                    input=True,
                    input_device_index=device.index,
                    frames_per_buffer=frames_per_buffer,
                )
        except Exception:
            for stream in opened.values():
                self._close_stream(stream)
            raise

        self._streams = opened

    def read(
        self,
        frames_per_buffer: int = 1024,
    ) -> dict[DeviceType, bytes]:
        
        if not self._streams:

            raise RuntimeError("No capture streams are open")
        
        if frames_per_buffer <= 0:
            raise ValueError("frames_per_buffer must be positive")

        return {
            device_type: stream.read(
                frames_per_buffer,
                exception_on_overflow=False,
            )
            for device_type, stream in self._streams.items()
        }

    def read_loop(
        self,
        frames_per_buffer: int = 1024,
    ) -> Iterator[dict[DeviceType, bytes]]:
        while self._streams:
            yield self.read(frames_per_buffer)

    def close(self) -> None:
        streams = tuple(self._streams.values())
        self._streams.clear()
        for stream in streams:
            self._close_stream(stream)


    @staticmethod
    def _close_stream(stream: Stream) -> None:
        if stream.is_active():
            stream.stop_stream()
        stream.close()
