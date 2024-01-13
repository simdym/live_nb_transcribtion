import threading
from datetime import datetime
import time

from channel_manager import ChannelManager, ChannelManagerConfig, RecordingThreadReady
from transcribtion import Transcriber, TranscriberConfig

def main():
    channel_manager_config = ChannelManagerConfig()
    transcriber_config = TranscriberConfig()

    channel_manager = ChannelManager(channel_manager_config)
    transcriber = Transcriber(transcriber_config)
    recording_thread_ready = RecordingThreadReady(channel_manager_config)

    channel_manager.add_channel("ch1")
    duration = 600
    channel_manager.channels["ch1"].start_recording(duration)
    print(channel_manager["ch1"].is_running())

    numpy_recordings = []
    transcribtions = []
    program_start = datetime.now()
    while True:

        ready_threads = channel_manager.get_ready_channels(recording_thread_ready)

        for channel_name in ready_threads:
            numpy_recordings.append(channel_manager[channel_name].get_audio())

        if numpy_recordings:
            print("Transcribing")
            start = datetime.now()
            recording = numpy_recordings.pop(0)
            transcribtion = transcriber.transcribe(recording)
            print(transcribtion.text)
            print(datetime.now() - start)


if __name__ == "__main__":
    main()