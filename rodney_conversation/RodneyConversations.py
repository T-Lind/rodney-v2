import os
from os.path import join, dirname

from dotenv import load_dotenv

from rodney_conversation.AzureFaceIdentifier import AzureFaceIdentifier
from rodney_conversation.AzureSpeechTranscriber import AzureSpeechTranscriber

dotenv_path = join(dirname(__file__), "./../.env")
load_dotenv(dotenv_path)


class RodneyConversations:
    def __init__(self):
        self.azure_face_identifier = AzureFaceIdentifier(os.environ.get("ENDPOINT"),
                                                         os.environ.get("AZURE_FACE_API_KEY"),
                                                         os.environ.get("AZURE_PERSON_GROUP_ID"))
        self.azure_face_identifier.start_identification()
        self.azure_face_identifier.pause_identification()

        self.transcriber = AzureSpeechTranscriber(os.environ.get("AZURE_SPEECH_API_KEY"),
                                                  os.environ.get("AZURE_SPEECH_REGION"))

    def
