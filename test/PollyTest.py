import os

import boto3
import pyaudio
from dotenv import load_dotenv

load_dotenv("./../.env")

aws_default_region = os.getenv("AWS_DEFAULT_REGION")


def play_speech_from_polly(text):
    polly_client = boto3.client('polly', region_name=aws_default_region)
    response = polly_client.synthesize_speech(Text=text, OutputFormat='pcm', VoiceId='Matthew')

    # Play audio directly
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(width=2),  # 2 bytes = 16 bits
                    channels=1,
                    rate=16000,  # Amazon Polly returns PCM audio at 16kHz
                    output=True)
    stream.write(response['AudioStream'].read())
    stream.stop_stream()
    stream.close()
    p.terminate()


# Example usage:
play_speech_from_polly("Hello, my name is Rodney!")
