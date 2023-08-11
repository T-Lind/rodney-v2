import queue
import threading

import azure.cognitiveservices.speech as speechsdk
import pyaudio


class AzureTextToSpeech:
    def __init__(self, subscription_key, region):
        self.subscription_key = subscription_key
        self.region = region
        self.text_queue = queue.Queue()
        self.running = False
        self.thread = None

    def _synthesize_and_play(self):
        speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.region)
        audio_config = speechsdk.AudioOutputConfig(use_default_speaker=True)  # Direct output to default speaker

        # Create a speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        p = pyaudio.PyAudio()

        while self.running:
            try:
                text = self.text_queue.get(timeout=1)
                result = speech_synthesizer.speak_text_async(text).get()

                if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                    print(f"Error synthesizing text: {text}")

            except queue.Empty:
                continue

        p.terminate()

    def start(self):
        if self.thread and self.thread.is_alive():
            print("Already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._synthesize_and_play)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def speak(self, text):
        self.text_queue.put(text)
