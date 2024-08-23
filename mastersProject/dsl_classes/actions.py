class HealAction:
    def __init__(self, amount):
        self.amount = amount

    def activate(self, player):
        player.heal(self.amount)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class RestoreManaAction:
    def __init__(self, amount):
        self.amount = amount

    def activate(self, player):
        player.restore_mana(self.amount)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)