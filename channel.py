import math
import threading
from datetime import datetime

from recording import NumpyRecording, Recorder, BinaryRecording

from abc import ABC, abstractmethod

class AudioChannel(ABC):
    """Audio channel which records and returns audio clips"""
    @abstractmethod
    def start_recording(self, duration: float):
        pass

    @abstractmethod
    def get_audio(self):
        pass


class SingleRecorderChannel(AudioChannel):
    def __init__(self, recorder: Recorder, channel_name: str) -> None:
        self.recorder = recorder
        self.channel_name = channel_name

        self._thread = None
        self._recording = None

    def start_recording(self, duration: float):
        """Start a thread that records from given recorder"""
        if self.recorder.is_recording:
            raise RuntimeError("Recorder is already recording")
        
        rec_start = datetime.now()
        self._recording = BinaryRecording(rec_start, self.channel_name)
        self._thread = threading.Thread(target=self.recorder.record, args=(duration, self._recording))
        self._thread.start()
    
    def get_audio(self, samples: int = None):
        """Gets numpy recording from thread"""
        return NumpyRecording(self._recording)
    
    def is_running(self):
        """Check if channel is running"""
        if self._thread is None:
            return False
        else:
            return self._thread.is_alive()
    
    def get_rec_len(self):
        if self._recording is None:
            return 0
        else:
            return len(self._recording)



if __name__ == "__main__":
    from recording import StreamParams
    import time

    stream_params = StreamParams()
    recorder = Recorder(stream_params)

    channel = SingleRecorderChannel(recorder, "test1")

    channel.start_recording(30)

    print(channel.is_running())

    while channel.is_running():
        if channel.get_rec_len() > 16000:
            audio = channel.get_audio()
