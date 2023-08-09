import threading
from queue import Queue
import azure.cognitiveservices.speech as speechsdk


class AzureSpeechTranscriber:
    def __init__(self, subscription_key, region):
        self.subscription_key = subscription_key
        self.region = region
        self.recognizer = None
        self.transcription_thread = None
        self.running = False
        self.pause_event = threading.Event()
        self.transcription_queue = Queue()

    def _transcribe(self):
        # Set up the subscription info for the Speech SDK
        speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.region)
        self.recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

        # Define event handlers
        self.recognizer.recognized.connect(self._recognized_handler)

        # Start continuous recognition
        self.recognizer.start_continuous_recognition()

        while self.running:
            self.pause_event.wait()

        # Stop continuous recognition
        self.recognizer.stop_continuous_recognition()

    def _recognized_handler(self, args):
        if args.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            self.transcription_queue.put(args.result.text)  # Enqueue the transcription

    def start(self):
        if self.transcription_thread:
            print("Transcription is already running.")
            return

        self.running = True
        self.pause_event.set()
        self.transcription_thread = threading.Thread(target=self._transcribe)
        self.transcription_thread.start()

    def stop(self):
        self.running = False
        if self.transcription_thread:
            self.transcription_thread.join()
            self.transcription_thread = None

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()

    def get_transcriptions(self):
        """Fetch all transcriptions currently in the queue."""
        transcriptions = []
        while not self.transcription_queue.empty():
            transcriptions.append(self.transcription_queue.get())
        return transcriptions


