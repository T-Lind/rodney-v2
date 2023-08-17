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
