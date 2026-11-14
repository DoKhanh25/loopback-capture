
from audio.audio_capture import AudioCapture
from queue import Queue
from threading import Thread
from audio.audio_preprocess import AudioPreprocess
from config import AudioConfig

class AudioCaptureWorker: 
    
    audio_capture: AudioCapture

    def __init__(
            self,
            audio_capture: AudioCapture,
            chunk_queue: Queue
        ):
        self.audio_capture: AudioCapture = audio_capture
        self.chunk_queue: Queue = chunk_queue
        self.thread: Thread = None


    def start(self):
        if self.thread and self.thread.is_alive(): 
            raise RuntimeError("AudioWorker is already running")

        self.audio_capture.prepare()

        self.thread = Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()

    def run(self):
        preprocess = AudioPreprocess(
            input_rate= AudioConfig.input_rate,
            output_rate= AudioConfig.output_rate,
            input_channels= AudioConfig.input_channel,
            chunk_duration_ms=AudioConfig.chunk_duration_ms
        )

        for chunk in self.audio_capture.capture():

            # Handling chunk after putting in Queue
            chunk = preprocess.process_mono(chunk) 
            chunk = preprocess.chunk_sample(chunk)

            self.chunk_queue.put(chunk)


    def stop(self): 
        if self.thread is None: 
            return

        self.audio_capture.request_stop_thread()
        self.thread.join()
        self.thread = None



