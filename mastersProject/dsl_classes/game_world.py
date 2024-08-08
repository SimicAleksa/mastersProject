from random import uniform
import random

from mastersProject.dsl_classes.item import Item
from mastersProject.dsl_classes.region import Region


class GameWorld:
    def __init__(self):
        self.regions = []
        self.items = {}
        self.enemies = []
        self.weapons = {}
        self.armors = {}
        self.player = None
        self.current_enemy = None
        self.start_position = None
        self.final_position = None
        self.prev_direction = None
        self.opposite_dirs = {"N": "S", "S": "N", "E": "W", "W": "E"}
        self.settings = None

    def generate_new_regions(self, num_regions):
        previous_region = None

        for i in range(num_regions):
            # Generisati naziv i opis pomocu CHAT GPT-a
            new_region_name = f"Region_{len(self.regions) + 1}"
            new_region_portrayal = f"A newly discovered area {new_region_name}."
            new_region = Region(new_region_name, new_region_portrayal)

            if previous_region:
                available_directions = [d for d in self.opposite_dirs.keys() if d not in previous_region.connections]

                if available_directions:
                    direction = random.choice(available_directions)
                    previous_region.add_connection(direction, new_region.name)
                    new_region.add_connection(self.opposite_dirs[direction], previous_region.name)

                # Dodatne konekcije ka vec postojecim regijama
                num_extra_connections = random.choice([0, 0, 0, 0, 1, 1, 1, 2])
                connected_regions = {previous_region}

                for _ in range(num_extra_connections):
                    existing_region = random.choice([r for r in self.regions if r not in connected_regions])
                    available_directions = [d for d in self.opposite_dirs.keys() if
                                            d not in existing_region.connections]

                    if available_directions:
                        direction = random.choice(available_directions)
                        existing_region.add_connection(direction, new_region.name)
                        new_region.add_connection(self.opposite_dirs[direction], existing_region.name)
                        connected_regions.add(existing_region)

            elif self.regions:
                existing_region = self.final_position
                available_directions = [d for d in self.opposite_dirs.keys() if d not in existing_region.connections]

                if available_directions:
                    direction = random.choice(available_directions)
                    existing_region.add_connection(direction, new_region.name)
                    new_region.add_connection(self.opposite_dirs[direction], existing_region.name)

            self.regions.append(new_region)
            previous_region = new_region

        self.set_final_position(previous_region)
        return previous_region

    # ChatGPT API TODO kasnije
    def generate_new_item(self):
        # Generisati naziv i opis pomocu CHAT GPT-a
        new_item_name = f"Item_{len(self.items) + 1}"
        new_item_portrayal = f"A mysterious object called {new_item_name}."
        new_item = Item(new_item_name, new_item_portrayal, is_static=False)

        # Dodati item u neku regiju (mozda dodati da se item stavlja u novokreirane regije)
        if self.regions:
            random_region = random.choice(self.regions)
            random_region.add_item(new_item)

        self.items[new_item_name] = new_item
        return new_item

    def explore_new_area(self):
        num_new_regions = random.randint(3, 9)
        last_region = self.generate_new_regions(num_new_regions)
        print(f"You've discovered {num_new_regions} new areas, with {last_region.name} being the furthest!")

    def check_combat(self, region):
        for enemy in self.enemies:
            if enemy.get_position() is not None:
                if enemy.get_position().name == region.name:
                    self.current_enemy = enemy
                    return True
        return False

    def set_start_position(self, region):
        self.start_position = region

    def set_final_position(self, region):
        self.final_position = region

    def flee(self):
        if self.current_enemy is not None:
            print("You fled!")
            self.current_enemy = None
            self.player.move(self.opposite_dirs[self.prev_direction], self)
            print(self.player.print_self())
        else:
            print("No reason to flee you coward!!!")

    def attack_enemy(self):
        damage = int(self.player.strike_damage() * uniform(0.7, 1.3))
        mana_damage = int(self.player.get_mana_damage() * uniform(0.7, 1.3))
        enemy_health = max(self.current_enemy.get_health() - damage, 0)
        enemy_mana = max(self.current_enemy.get_mana() - mana_damage, 0)

        self.current_enemy.set_health(enemy_health)
        self.current_enemy.set_mana(enemy_mana)

        if self.player.weapon is not None:
            self.player.mana -= self.player.weapon.mana_cost
            self.player.health -= self.player.weapon.health_cost
            if self.player.weapon.mana_cost > 0:
                print(f"You have {self.player.mana} mana left")
            if self.player.weapon.health_cost > 0:
                print(f"You have {self.player.health} health left")
        print(f"You dealt {damage} damage. Enemy has {self.current_enemy.get_health()} health.")
        if enemy_health == 0:
            print(f"You beat {self.current_enemy.name}!")
            self.current_enemy.set_position_none()
            self.player.monster_slain(self.current_enemy)
            dropped_items = self.current_enemy.get_droppable()
            for item in dropped_items:
                self.player.position.items[item.name] = item
            if len(dropped_items) > 0:
                print(f"{self.current_enemy.name} dropped {', '.join([item.name for item in dropped_items])}")
            self.current_enemy = None
        else:
            self.heal_enemy()
            print(self.attack_player())

    def attack_player(self):
        chosen_attack = self.current_enemy.choose_attack()
        damage_variance_low = 1 - chosen_attack['health_damage_variance']
        damage_variance_high = 1 + chosen_attack['health_damage_variance']
        damage = int(chosen_attack['health_damage'] * uniform(damage_variance_low, damage_variance_high))

        mana_damage_variance_low = 1 - chosen_attack['mana_damage_variance']
        mana_damage_variance_high = 1 + chosen_attack['mana_damage_variance']
        mana_damage = int(chosen_attack['mana_damage'] * uniform(mana_damage_variance_low, mana_damage_variance_high))

        defense = int(self.player.get_defense() * uniform(0.7, 1.3))
        mana_defence = int(self.player.get_mana_defense() * uniform(0.7, 1.3))

        player_health = max(self.player.get_health() - max(damage - defense, 0), 0)
        player_mana = max(self.player.get_mana() - max(mana_damage - mana_defence, 0), 0)

        self.player.set_health(player_health)
        self.player.set_mana(player_mana)
        text = f"{self.current_enemy.name}'s turn.\n{self.current_enemy.name} dealt {damage} damage. You have {self.player.get_health()} health."
        # TODO: print player mana stats
        self.current_enemy.reduce_health(chosen_attack["health_cost"])
        self.current_enemy.reduce_mana(chosen_attack["mana_cost"])
        # TODO: print enemy stats
        if player_health == 0:
            text += "\nYou died"
            dropped_items_text = self.player.drop_items_after_death(self)
            text_val, _ = self.player.move_to_start_position(self)
            text += f"\n{text_val}"
            text += f"\n{dropped_items_text}"
            self.current_enemy.reset_health()
            self.current_enemy = None
        return text

    def heal_enemy(self):
        if self.current_enemy is not None and uniform(0, 1) < self.current_enemy.healing_chance:
            healing_variance_low = 1 - self.current_enemy.healing_amount_variance
            healing_variance_high = 1 + self.current_enemy.healing_amount_variance
            amount = int(self.current_enemy.healing_amount * uniform(healing_variance_low, healing_variance_high))
            self.current_enemy.heal(amount)
            print(f"Enemy healed by {amount}. Enemy has {self.current_enemy.get_health()} health.")
