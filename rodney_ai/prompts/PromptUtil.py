from langchain.prompts import load_prompt


def filter_irrelevant_locations_template(directive, locations_and_names, location_history):
    prompt = load_prompt("C:/Users/tenant/PycharmProjects/rodney-v2/rodney_ai/prompts/filter_irrelevant_locations.yaml")
    input_txt = prompt.format(directive=directive, locations_and_names=locations_and_names,
                              location_history=location_history,
                              example_1="{\n    \"building_name\": \"ZACH\"\n}",
                              example_2="{\n    \"building_name\": \"\"\n}")
    return input_txt


def choose_location_template(directive, locations_and_names, location_history):
    prompt = load_prompt("C:/Users/tenant/PycharmProjects/rodney-v2/rodney_ai/prompts/choose_location.yaml")
    input_txt = prompt.format(directive=directive, locations_and_names=locations_and_names,
                              location_history=location_history,
                              example_1="{\n    \"building_name\": \"ZACH\"\n}\n",
                              example_2="{\n    \"building_name\": \"\"\n    \"reasoning\":\"\"\n}\n")
    return input_txt


def log_location_template(building_name, date_and_time):
    prompt = load_prompt(r"C:\Users\tenant\PycharmProjects\rodney-v2\rodney_ai\prompts\location_history.yaml")
    input_txt = prompt.format(building_name=building_name, date_and_time=date_and_time)
    return input_txt


def printf(text, color=None, type=None):
    """
    Print colored and optionally styled text to the console using ANSI escape codes.

    :param text: The text to be printed
    :param color: The color of the text ('red', 'green', etc.)
    :param type: The text style ('bold', 'italic', etc.)
    """

    # Define color codes
    colors = {
        'reset': "\033[0m",
        'red': "\033[31m",
        'green': "\033[32m"
    }

    # Define type (style) codes
    types = {
        'reset': "\033[0m",
        'bold': "\033[1m",
        'italic': "\033[3m"
    }

    # Construct the print output
    color_code = colors.get(color, '')
    type_code = types.get(type, '')
    end_code = colors['reset']

    print(f"{color_code}{type_code}{text}{end_code}")
