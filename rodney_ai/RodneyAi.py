from datetime import datetime
from langchain.chat_models import ChatOpenAI

from rodney_ai.GPTChatCompleter import get_gpt_completions
from rodney_ai.LocationData import LocationData
from rodney_ai.prompts.PromptUtil import choose_location_template, printf, \
    log_location_template

from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), "./../.env")
load_dotenv(dotenv_path)


class RodneyAi:
    def __init__(self, directive, verbose=False, model_name="gpt-3.5-turbo"):
        self.directive = directive
        self.verbose = verbose
        self.model_name = model_name
        self.chatbot_ai = ChatOpenAI(temperature=0.0, max_tokens=100, model_name=model_name,
                                     openai_api_key=os.environ.get("OPENAI_API_KEY"))

        self.location_data = LocationData()

        self.location_history = []

    def _filter_irrelevant_locations(self, locations_and_names):
        # TODO: determine if this needs to be implemented
        return locations_and_names
        # model_input = filter_irrelevant_locations_template(self.directive,
        #                                                    locations_and_names, self.location_history)
        # model_output = get_gpt_completions(model_input)
        #
        # if self.verbose:
        #     printf(model_output, color="green", type="italic")
        #     printf(model_output, color="red", type="bold")
        # return model_output

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
