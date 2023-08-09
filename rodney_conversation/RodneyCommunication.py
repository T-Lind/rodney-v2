import os
from os.path import join, dirname
from dotenv import load_dotenv

from langchain.chat_models.openai import ChatOpenAI

from rodney_conversation.AzureDatabase import AzureDatabase
from rodney_conversation.AzureFaceIdentifier import AzureFaceIdentifier
from rodney_conversation.AzureSpeechTranscriber import AzureSpeechTranscriber
from rodney_conversation.AzureTextToSpeech import AzureTextToSpeech

dotenv_path = join(dirname(__file__), "./../.env")
load_dotenv(dotenv_path)


class RodneyCommunication:
    def __init__(self):
        self.azure_face_identifier = AzureFaceIdentifier(os.environ.get("ENDPOINT"),
                                                         os.environ.get("AZURE_FACE_API_KEY"),
                                                         os.environ.get("AZURE_PERSON_GROUP_ID"))
        self.azure_face_identifier.start_identification()
        self.azure_face_identifier.pause_identification()

        self.face_database = AzureDatabase()

        self.transcriber = AzureSpeechTranscriber(os.environ.get("AZURE_SPEECH_API_KEY"),
                                                  os.environ.get("AZURE_SPEECH_REGION"))

        self.tts = AzureTextToSpeech(os.environ.get("AZURE_SPEECH_API_KEY"),
                                     os.environ.get("AZURE_SPEECH_REGION"))
