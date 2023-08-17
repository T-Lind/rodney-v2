import os

from langchain.prompts import load_prompt

current_directory = os.path.dirname(os.path.abspath(__file__))


def initial_convo_prompt(directive):
    prompt = load_prompt(current_directory + "\\initial_convo.yaml")
    return prompt.format(directive=directive)


def notes_prompt(directive):
    prompt = load_prompt(current_directory + "\\notes_prompt.yaml")
    return prompt.format(directive=directive)
