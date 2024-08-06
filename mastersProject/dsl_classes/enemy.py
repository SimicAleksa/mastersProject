import numpy as np


class Enemy:
    def __init__(self, name, portrayal, position, health, mana, xp):
        self.name = name
        self.portrayal = portrayal
        self.position = position
        self.health = health
        self.initial_health = health

        self.mana = mana
        self.initial_mana = mana
        self.xp = xp

        self.items_to_drop = {}
        self.attacks = []

        self.healing_chance = 0
        self.healing_amount = 0
        self.healing_amount_variance = 0

    def get_xp_value(self):
        return self.xp

    def get_position(self):
        return self.position

    def set_position_none(self):
        self.position = None

    def get_description(self):
        return self.portrayal

    def get_health(self):
        return self.health

    def get_mana(self):
        return self.mana

    def set_health(self, value):
        self.health = value

    def set_mana(self, value):
        self.mana = value

    def reduce_health(self, value):
        self.health -= value

    def reduce_mana(self, value):
        self.mana -= value

    def heal(self, value):
        self.health = min(self.initial_health, self.health + value)

    def reset_health(self):
        self.set_health(self.initial_health)

    def get_droppable(self):
        result = []
        for i in self.items_to_drop:
            result.append(self.items_to_drop[i])
        return result

    def choose_attack(self):
        feasible_attacks = []
        for attack in self.attacks:
            if attack["health_cost"] < self.get_health() and attack["mana_cost"] <= self.get_mana():
                feasible_attacks.append(attack)
        # TODO: handle case when no feasible attacks
        if len(feasible_attacks) == 1:
            return feasible_attacks[0]
        attack_probabilities = [attack['frequency'] for attack in feasible_attacks]
        normalized_probabilities = np.array(attack_probabilities) / sum(attack_probabilities)
        return np.random.choice(feasible_attacks, p=normalized_probabilities)

    def print_self(self):
        return f'There is an enemy: {self.name}.'
