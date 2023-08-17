import pyaudio
import wave

# Parameters
channels = 1            # Number of audio channels (1 for mono)
sample_width = 2        # Sample width in bytes (2 for 16-bit audio)
sample_rate = 32000     # Sample rate in Hz

chunk_size = 1024       # Number of frames per buffer
record_seconds = 20      # Duration of the recording in seconds
output_filename = "recorded_audio.wav"

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream for recording
stream = p.open(format=p.get_format_from_width(sample_width),
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size)

print("Recording...")

frames = []

# Record audio data in chunks
for _ in range(0, int(sample_rate / chunk_size * record_seconds)):
    data = stream.read(chunk_size)
    frames.append(data)

print("Recording done.")

# Close and terminate the audio stream and PyAudio
stream.stop_stream()
stream.close()
p.terminate()

# Save the recorded audio to a WAV file
with wave.open(output_filename, 'wb') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))

print(f"Audio saved as {output_filename}")
