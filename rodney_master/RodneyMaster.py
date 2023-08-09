from rodney_ai.RodneyAi import RodneyAi


class RodneyMaster:
    def __init__(self, directive):
        self.ai = RodneyAi(directive)

        self.current_building = self.ai.select_next_location()
