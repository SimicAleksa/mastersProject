import numpy as np

class Weapon:
    def __init__(self, name, portrayal, weaponType, health_damage, mana_damage, health_cost, mana_cost, required_level):
        self.name = name
        self.portrayal = portrayal
        self.type = weaponType
        self.health_damage = health_damage
        self.mana_damage = mana_damage
        self.health_cost = health_cost
        self.mana_cost = mana_cost
        self.required_level = required_level
        self.modifiers = {}

    def add_modifier(self, attr_name, coefficients):
        self.modifiers[attr_name] = coefficients

    def print_with_modifiers(self, player):
        text = f'{self.portrayal}\nType: {self.type}\nAdditional health damage: {self.health_damage}\nAdditional mana damage: {self.mana_damage}'
        if self.health_cost > 0:
            text += f'\nReduces health by {self.health_cost} when used.'
        if self.mana_cost > 0:
            text += f'\nReduces mana by {self.mana_cost} when used.'
        for stat, coefficients in self.modifiers.items():
            stat_str = stat.replace('_', ' ')
            text += f'\nModifies {stat_str}: {player.__getattribute__(stat)} -> {np.polyval(coefficients, player.__getattribute__(stat))}'
        return text
