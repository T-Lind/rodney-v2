import re
from datetime import datetime
from os.path import join, dirname

from dotenv import load_dotenv

from rodney_ai.Chatbot import Chatbot
from rodney_ai.GPTChatCompleter import get_gpt_completions
from rodney_ai.LocationData import LocationData
from rodney_ai.prompts.PromptUtil import choose_location_template, \
    log_location_template, conversation_template
from rodney_conversation.printf import printf
from rodney_conversation.RodneyCommunication import RodneyCommunication

dotenv_path = join(dirname(__file__), "./../.env")
load_dotenv(dotenv_path)


class Conversation:
    def __init__(self, directive, person_info, location):
        if person_info:
            self.name = person_info["Name"]
            self.notes = person_info["Notes"]
        else:
            self.name = self.notes = ""
        self.chatbot = Chatbot(system_prompt=conversation_template(directive, self.name, location, self.notes))


class RodneyAi:
    def __init__(self, directive, verbose=False, model_name="gpt-3.5-turbo"):
        self.directive = directive
        self.verbose = verbose
        self.model_name = model_name
        self.conversation = None

        self.location_data = LocationData()

        self.communication = RodneyCommunication()

        self.location_history = []

    def _filter_irrelevant_locations(self, locations_and_names):
        # TODO: determine if this needs to be implemented
        return locations_and_names

    def select_next_location(self):
        model_input = choose_location_template(self.directive, self.location_data.get_file_text(),
                                               str(self.location_history))
        model_output = get_gpt_completions(model_input)

        if self.verbose:
            printf(model_input, color="green", type="italic")
            printf(model_output, color="red", type="italic")

        gps_coordinate, building_name = self.location_data.get_gps_coordinate_json(model_output)

        currently = datetime.now()
        formatted_datetime = currently.strftime("%B %d, %Y, %H: %M")

        self.location_history.append(log_location_template(building_name, formatted_datetime))
        # should be like [29.3, -30.4], "ZACH"
        return gps_coordinate

    def init_conversation(self):
        self.communication.azure_face_identifier.start_identification()
        self.communication.tts.start()

    def start_conversation(self):
        # Ensure that all services are running
        self.communication.azure_face_identifier.resume_identification()
        self.communication.transcriber.start_transcription()
        self.communication.tts.start()

        detected_uuids = self.communication.azure_face_identifier.get_detected_uuids()
        person_info = None
        uuid = None
        if detected_uuids:
            uuid = detected_uuids[0]  # considering only the first detected UUID
            person_info = self.communication.face_database.retrieve_person_info(
                uuid)
            if person_info:
                if len(detected_uuids) > 1:
                    self.communication.tts.speak(
                        "I'm sorry, I can only speak to one person at a time, " + person_info["Name"])

        my_location = self.location_history[-1]
        self.conversation = Conversation(self.directive, person_info,
                                         f"{self.location_history[-1]}: {self.location_data.get_description(my_location)}")

        introduction = self.conversation.chatbot.ask(
            "You're initiating the conversation, so start off with an appropriate introduction based on the system message above.")
        self.communication.tts.speak(introduction)

        while True:
            # 1. Wait for a new transcription (this can be blocking as we are in a loop)
            transcriptions = self.communication.transcriber.get_transcriptions()
            if not transcriptions:
                continue

            user_input = transcriptions[0]  # Take the first transcription (consider merging if there are multiple)

            # 2. Feed the transcription to the Chatbot
            chatbot_response = self.conversation.chatbot.ask(user_input)

            # 3. Check if the Chatbot wants to end the conversation & names
            matches = re.findall(r'\[(.*?)\]', chatbot_response)
            should_end = False
            for text in matches:
                if text == "END":
                    if self.communication.face_database.retrieve_person_info(uuid):
                        notes = self.conversation.chatbot.ask(
                            "The end of the conversation has come. Please write some notes about your interaction "
                            "with this person and what you discussed. Keep it as short as possible, but include "
                            "important details related to your directive.")
                        self.communication.face_database.update_person_notes(uuid, notes)
                    should_end = True
                else:
                    self.communication.face_database.insert_person_info(uuid, text, notes="")

            # 4. Speak out the Chatbot's response
            self.communication.tts.speak(chatbot_response)

            if should_end:
                self.communication.tts.speak("Exiting the conversation. Thank you for your time")
                break

        # Stop the services after the conversation ends
        self.communication.azure_face_identifier.pause_identification()
        self.communication.transcriber.stop_transcription()
        self.communication.tts.stop()
