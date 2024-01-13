from dataclasses import dataclass

from channel import SingleRecorderChannel
from recording import StreamParams, Recorder
from typing import Any, Callable


@dataclass
class ChannelManagerConfig:
    min_rec_length_for_extraction: int = 16000 * 10 # 5s


class RecordingThreadReady():
    """Callable class to determine if we should extract samples from recording thread"""

    def __init__(self, config: ChannelManagerConfig) -> None:
        self.config = config
    

    def __call__(self, thread, recording):
        if len(recording) > self.config.min_rec_length_for_extraction:
            return True
        elif not thread.is_alive():
            return True
        else:
            return False


class ChannelManager():
    def __init__(self, config: ChannelManagerConfig):
        self.config = config
        self.channels = {}

        self.recordings_for_processing = {}

    def add_channel(self, channel_name: str):
        self.channels[channel_name] = SingleRecorderChannel(
            Recorder(StreamParams()),
            channel_name=channel_name
        )

    def __getitem__(self, key: Any):
        return self.channels[key]

    def get_ready_channels(self, disc_function: Callable):
        """Get threads which fulfills some conditon"""
        ready_channels = []

        for channel_name, channel in self.channels.items():
            if disc_function(channel._thread, channel._recording):
                ready_channels.append(channel_name)
        
        return ready_channels
        
