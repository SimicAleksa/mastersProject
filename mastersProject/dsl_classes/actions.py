class HealAction:
    def __init__(self, amount):
        self.amount = amount

    def activate(self, player):
        player.heal(self.amount)


class RestoreManaAction:
    def __init__(self, amount):
        self.amount = amount

    def activate(self, player):
        player.restore_mana(self.amount)