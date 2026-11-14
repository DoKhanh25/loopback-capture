from collections.abc import Iterator
from threading import Event

import pyaudiowpatch as pyaudio
from pyaudiowpatch import PyAudio, Stream

from audio.device_manager import DeviceManager
from dto.audio_device import DeviceType
from config import AudioConfig



class AudioCapture:

    def __init__(
        self,
        audio: PyAudio,
        device_manager: DeviceManager,
    ):
        self.audio = audio
        self.device_manager = device_manager
        self._stop_event = Event()
        self._streams: dict[DeviceType, Stream] = {}


    """
    Prepare new capture session.
    Must be called after starting the capture thread.
    """
    def prepare(self) -> None:
        if DeviceType.LOOPBACK in self._streams: 
            raise RuntimeError("Capture is already running")

        self._stop_event.clear()


    """
    Capture sound from device loopback
    """
    def capture(
        self,
        *,
        loopback: bool = True,
        sample_rate: int = AudioConfig.input_rate,
        channels: int = AudioConfig.input_channel,
        frames_per_buffer: int = AudioConfig.frames_per_buffer,
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
            while not self._stop_event.is_set():

                audio_chunk = stream.read(
                    num_frames=frames_per_buffer,
                    exception_on_overflow=False,
                )

                yield audio_chunk

        finally:
            self.cleanup(stream=stream)


    def request_stop_thread(self): 
        self._stop_event.set()


    def cleanup(self, stream: Stream) -> None: 

        self._streams.pop(DeviceType.LOOPBACK, None)
        
        if stream.is_active(): 
            stream.stop_stream()

        stream.close()

