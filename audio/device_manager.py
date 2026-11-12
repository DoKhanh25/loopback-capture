from pyaudiowpatch import PyAudio
import pyaudiowpatch as pyaudio
from dto.audio_device import AudioDevice, DeviceType
from audio.audio_context import AudioContext


class DeviceManager: 

    def __init__(self, audio: PyAudio ):
        self.audio: PyAudio = audio

    def list_devices(self) -> list[AudioDevice]: 
        devices = []

        loopbacks = {
            d["index"]: d for d in self.audio.get_loopback_device_info_generator()
        }

        for i in range(self.audio.get_device_count()): 
            info = self.audio.get_device_info_by_index(i)

            if i in loopbacks: 
                device_type = DeviceType.LOOPBACK

            elif info["maxInputChannels"] > 0:
                device_type = DeviceType.MICROPHONE

            else: 
                continue

            devices.append(self._to_audio_device(info=info, device_type=device_type))

        return devices

    def list_input_devices(self) -> list[AudioDevice]:

        return [
            d for d in self.list_devices()
            if d.device_type == DeviceType.MICROPHONE
        ]


    def list_loopback_devices(self) -> list[AudioDevice]:

        return [
            d for d in self.list_devices()
            if d.device_type == DeviceType.LOOPBACK
        ]

    def get_default_microphone(self) -> AudioDevice:

        info = self.audio.get_default_input_device_info()

        return self._to_audio_device(
            info,
            DeviceType.MICROPHONE
        )

    def get_default_loopback(self) -> AudioDevice:

        info = self.audio.get_default_wasapi_loopback()

        return self._to_audio_device(
            info,
            DeviceType.LOOPBACK
        )

    def get_device_info(self, index: int) -> AudioDevice:

        info = self.audio.get_device_info_by_index(index)

        loopback_indices = {
            d["index"]
            for d in self.audio.get_loopback_device_info_generator()
        }

        if index in loopback_indices:
            device_type = DeviceType.LOOPBACK

        elif info["maxInputChannels"] > 0:
            device_type = DeviceType.MICROPHONE

        else:
            raise ValueError("Device is not an input device")

        return self._to_audio_device(info, device_type)



    def validate_device(self, device: AudioDevice) -> bool:

        try:
            self.audio.is_format_supported(
                device.sample_rate,
                input_device=device.index,
                input_channels=device.channels,
                input_format=pyaudio.paInt16
            )

            return True

        except ValueError:
            return False



    def _to_audio_device(
        self,
        info: dict,
        device_type: DeviceType
    ) -> AudioDevice:

        host_api_info = self.audio.get_host_api_info_by_index(
            info["hostApi"]
        )

        return AudioDevice(
            index=int(info["index"]),
            name=info["name"],
            device_type=device_type,
            host_api=host_api_info["name"],
            sample_rate=int(info["defaultSampleRate"]),
            channels=int(info["maxInputChannels"]),
        )



