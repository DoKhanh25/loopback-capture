import pyaudiowpatch as pyaudio
from pyaudiowpatch import PyAudio


# Initialize Singleton Audiocontext
class AudioContext: 

    def __init__(self): 
        self._audio: PyAudio = pyaudio.PyAudio() 

    @property
    def audio(self) -> PyAudio:
        return self._audio

    def close(self):
        self._audio.terminate()