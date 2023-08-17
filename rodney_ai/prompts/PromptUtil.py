import os

from langchain.prompts import load_prompt

current_directory = os.path.dirname(os.path.abspath(__file__))


def filter_irrelevant_locations_template(directive, locations_and_names, location_history):
    prompt = load_prompt(current_directory + "\\filter_irrelevant_locations.yaml")
    input_txt = prompt.format(directive=directive, locations_and_names=locations_and_names,
                              location_history=location_history,
                              example_1="{\n    \"building_name\": \"ZACH\"\n}",
                              example_2="{\n    \"building_name\": \"\"\n}")
    return input_txt


def choose_location_template(directive, locations_and_names, location_history):
    prompt = load_prompt(current_directory + "\\choose_location.yaml")
    input_txt = prompt.format(directive=directive, locations_and_names=locations_and_names,
                              location_history=location_history,
                              example_1="{\n    \"building_name\": \"ZACH\"\n}\n",
                              example_2="{\n    \"building_name\": \"\"\n    \"reasoning\":\"\"\n}\n")
    return input_txt


def log_location_template(building_name, date_and_time):
    prompt = load_prompt(current_directory + "\\location_history.yaml")
    input_txt = prompt.format(building_name=building_name, date_and_time=date_and_time)
    return input_txt


def conversation_template(directive, person_name, location, notes):
    prompt = load_prompt(current_directory + "\\conversation.yaml")
    input_txt = prompt.format(directive=directive, person_name=person_name, location=location, notes=notes)
    return input_txt