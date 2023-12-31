import collections
import contextlib
import os
import sys
import time
import wave

import numpy as np
import pyaudio
import webrtcvad


class VAD:
    @staticmethod
    def read_wave(path):
        """Reads a .wav file.

        Takes the path, and returns (PCM audio data, sample rate).
        """
        with contextlib.closing(wave.open(path, 'rb')) as wf:
            num_channels = wf.getnchannels()
            assert num_channels == 1
            sample_width = wf.getsampwidth()
            assert sample_width == 2
            sample_rate = wf.getframerate()
            assert sample_rate in (8000, 16000, 32000, 48000)
            pcm_data = wf.readframes(wf.getnframes())
            return pcm_data, sample_rate

    @staticmethod
    def write_wave(path, audio, sample_rate):
        """Writes a .wav file.

        Takes path, PCM audio data, and sample rate.
        """
        print(f"Writing audio to path {path}")

        with contextlib.closing(wave.open(path, 'wb')) as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio)

    class Frame(object):
        """Represents a "frame" of audio data."""

        def __init__(self, bytes, timestamp, duration):
            self.bytes = bytes
            self.timestamp = timestamp
            self.duration = duration

    @staticmethod
    def frame_generator(frame_duration_ms, audio, sample_rate):
        """Generates audio frames from PCM audio data.

        Takes the desired frame duration in milliseconds, the PCM data, and
        the sample rate.

        Yields Frames of the requested duration.
        """
        n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
        offset = 0
        timestamp = 0.0
        duration = (float(n) / sample_rate) / 2.0
        while offset + n < len(audio):
            yield VAD.Frame(audio[offset:offset + n], timestamp, duration)
            timestamp += duration
            offset += n

    @staticmethod
    def vad_collector(sample_rate, frame_duration_ms,
                      padding_duration_ms, vad, frames):
        """Filters out non-voiced audio frames.

        Given a webrtcvad.Vad and a source of audio frames, yields only
        the voiced audio.

        Uses a padded, sliding window algorithm over the audio frames.
        When more than 90% of the frames in the window are voiced (as
        reported by the VAD), the collector triggers and begins yielding
        audio frames. Then the collector waits until 90% of the frames in
        the window are unvoiced to detrigger.

        The window is padded at the front and back to provide a small
        amount of silence or the beginnings/endings of speech around the
        voiced frames.

        Arguments:

        sample_rate - The audio sample rate, in Hz.
        frame_duration_ms - The frame duration in milliseconds.
        padding_duration_ms - The amount to pad the window, in milliseconds.
        vad - An instance of webrtcvad.Vad.
        frames - a source of audio frames (sequence or generator).

        Returns: A generator that yields PCM audio data.
        """
        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        # We use a deque for our sliding window/ring buffer.
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
        # NOTTRIGGERED state.
        triggered = False

        voiced_frames = []
        for frame in frames:
            is_speech = vad.is_speech(frame.bytes, sample_rate)

            sys.stdout.write('1' if is_speech else '0')
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                # If we're NOTTRIGGERED and more than 90% of the frames in
                # the ring buffer are voiced frames, then enter the
                # TRIGGERED state.
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                    # We want to yield all the audio we see from now until
                    # we are NOTTRIGGERED, but we have to start with the
                    # audio that's already in the ring buffer.
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                # We're in the TRIGGERED state, so collect the audio data
                # and add it to the ring buffer.
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                # If more than 90% of the frames in the ring buffer are
                # unvoiced, then enter NOTTRIGGERED and yield whatever
                # audio we've collected.
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                    triggered = False
                    yield b''.join([f.bytes for f in voiced_frames])
                    ring_buffer.clear()
                    voiced_frames = []
        if triggered:
            sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
        sys.stdout.write('\n')
        # If we have any leftover voiced audio when we run out of input,
        # yield it.
        if voiced_frames:
            yield b''.join([f.bytes for f in voiced_frames])

    @staticmethod
    def capture_audio_from_microphone(sample_rate=16000, chunk_size=1024, num_chunks=10):
        audio_data = []

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Open a microphone stream
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size)

        print("Capturing audio from the microphone...")

        for _ in range(num_chunks):
            audio_chunk = stream.read(chunk_size)
            audio_data.append(np.frombuffer(audio_chunk, dtype=np.int16))

        # Close the stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Convert the audio data into a single numpy array
        audio_data = np.concatenate(audio_data)

        return audio_data

    @staticmethod
    def capture_and_segment_audio(audio_file_path, vad=webrtcvad.Vad(3), frame_duration_ms=30, sample_rate=16000, min_capture_duration=3000):
        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Open a microphone stream
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=int(sample_rate * frame_duration_ms / 1000))

        audio_buffer = []  # Buffer to store audio chunks
        start_time = None

        print("Capturing audio from the microphone...")

        capturing = True  # Flag to indicate if audio is being captured

        while True:
            audio_chunk = stream.read(int(sample_rate * frame_duration_ms / 1000))
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)

            if vad.is_speech(audio_chunk, sample_rate):
                start_time = time.time()
                if not capturing:
                    print("Speech detected, capturing...")
                    capturing = True
                audio_buffer.extend(audio_data)
            else:
                if capturing and len(audio_buffer) > 0:
                    if time.time() - start_time >= min_capture_duration / 1000:
                        print("End of speech detected, saving audio...")
                        VAD.write_wave(audio_file_path, np.array(audio_buffer), sample_rate)
                        audio_buffer = []  # Reset the audio buffer
                        capturing = False

            # Check for stopping condition (end loop if no more audio is being captured)
            if not capturing:
                break


        # Close the stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()
