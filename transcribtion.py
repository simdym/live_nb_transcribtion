from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from transformers import pipeline

from recording import NumpyRecording

from typing import List

class Transcribtion():
    def __init__(self, channel_name: str, start: datetime, end: datetime, text: str):
        self.channel_name = channel_name
        self.start = start
        self.end = end
        self.text = text

@dataclass
class WhisperConfig:
    task: str = "transcribe"
    language: str = "no"

@dataclass
class WhisperPipelineConfig:
    task: str = "automatic-speech-recognition"
    model: str = "NbAiLab/nb-whisper-small-beta"

@dataclass
class TranscriberConfig:
    pipeline_config = WhisperPipelineConfig()
    model_config = WhisperConfig()
    sr: float = 16000


class Transcriber():
    def __init__(self, config: TranscriberConfig):
        self.config = config
        self.pipeline = pipeline(
            **asdict(self.config.pipeline_config)
        )
    
    def transcribe(self, recording: NumpyRecording):
        pipeline_output = self.pipeline(
            {"raw": recording.waveform, "sampling_rate": self.config.sr},
            generate_kwargs = asdict(self.config.model_config)
        )

        duration = timedelta(seconds=len(recording) / self.config.sr)

        return Transcribtion(
            channel_name = recording.channel_name,
            start=recording.start,
            end=recording.start + duration,
            text = pipeline_output["text"]
        )
        