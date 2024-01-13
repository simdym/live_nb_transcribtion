from dataclasses import dataclass, asdict
import pyaudio
import numpy as np
import datetime

@dataclass
class StreamParams:
    format: int = pyaudio.paFloat32
    channels: int = 1
    rate: int = 16000
    frames_per_buffer: int = 1024
    input: bool = True
    output: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
    

class BinaryRecording():
    def __init__(self, start: datetime, channel_name: str):
        self.start = start
        self.channel_name = channel_name
        self.buffer = bytearray()
        self.bytes_per_value = int(32/8)
    
    def add_to_buffer(self, bytearray):
        self.buffer.extend(bytearray)
    
    def extract_samples(self, samples):
        return self.buffer[:samples * self.bytes_per_value]
    
    def delete_samples(self, samples):
        del self.buffer[:samples * self.bytes_per_value]
    
    def __len__(self):
        return int(len(self.buffer) / self.bytes_per_value)


class NumpyRecording():
    def __init__(self, binary_recording: BinaryRecording, samples: int = None, delete: bool = True):
        """Extract contents as numpy array"""

        if samples is None: # If none extract all
            samples = len(binary_recording)

        if len(binary_recording) < samples:
            raise MemoryError("Requested length is longer than buffer length")

        self.start = binary_recording.start
        self.channel_name = binary_recording.channel_name
        self.dtype = np.float32

        extracted_samples = binary_recording.extract_samples(samples)
        if delete:
            binary_recording.delete_samples(samples)

        self.waveform = np.frombuffer(extracted_samples, self.dtype)
    
    def __len__(self):
        return len(self.waveform)


class Recorder():
    """Records audio"""

    def __init__(self, stream_params: StreamParams):
        self.stream_params = stream_params
        self._pyaudio = None
        self._stream = None

        self.is_recording = False
    
    def record(self, duration: float, recording: BinaryRecording):
        self.is_recording = True
        self._create_recording_ressources()
        
        for _ in range(int(self.stream_params.rate * duration / self.stream_params.frames_per_buffer)):
            audio_data = self._stream.read(self.stream_params.frames_per_buffer)
            recording.add_to_buffer(audio_data)

        self._close_recording_ressources()
        self.is_recording = False

    def _create_recording_ressources(self):
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(**self.stream_params.to_dict())

    def _close_recording_ressources(self):
        self._stream.close()
        self._pyaudio.terminate()





if __name__ == "__main__":
    import threading
    import time
    from datetime import datetime

    def print_buffer_length(recording, period = 2):
        samples = 1000
        for i in range(6):
            time.sleep(2)
            print(len(recording))

    recording = BinaryRecording("test", datetime.now())

    stream_params = StreamParams()
    recorder = Recorder(stream_params)

    recorder_thread = threading.Thread(target=recorder.record, args=(10,recording))
    printing_thread = threading.Thread(target=print_buffer_length, args=(recording,))

    recorder_thread.start()
    printing_thread.start()

    while recorder_thread.is_alive():
        pass
        print(recorder_thread.is_alive())
        time.sleep(1)
    
    print(NumpyRecording(recording).waveform.shape)