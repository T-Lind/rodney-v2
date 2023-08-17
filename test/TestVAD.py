import os
import webrtcvad
from rodney_conversation.VAD import VAD


filename = "recorded_audio.wav"
audio, sample_rate = VAD.read_wave(filename)
vad = webrtcvad.Vad(1)
frames = VAD.frame_generator(30, audio, sample_rate)
frames = list(frames)
segments = VAD.vad_collector(sample_rate, 30, 300, vad, frames)

# Create a directory for storing chunks
output_dir = os.path.splitext(filename)[0] + "_vad"
os.makedirs(output_dir, exist_ok=True)

for i, segment in enumerate(segments):
    path = os.path.join(output_dir, f'chunk-{i:02d}.wav')
    print(' Writing %s' % (path,))
    VAD.write_wave(path, segment, sample_rate)
