class GeneralSettings:
    def __init__(self, drop_other_weapons, drop_other_armors, additional_turn_after_use):
        self.drop_other_weapons = drop_other_weapons
        self.drop_other_armors = drop_other_armors
        self.additional_turn_after_use = additional_turn_after_use

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)