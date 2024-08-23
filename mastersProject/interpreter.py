from textx import metamodel_from_file
from os.path import join, dirname

from mastersProject.dsl_classes.game_world import GameWorld
from mastersProject.dsl_classes.player import Player
from mastersProject.dsl_classes.region import Region
from mastersProject.dsl_classes.enemy import Enemy
from mastersProject.dsl_classes.item import Item
from mastersProject.dsl_classes.weapon import Weapon
from mastersProject.dsl_classes.armor import Armor
from mastersProject.dsl_classes.actions import HealAction, RestoreManaAction
from mastersProject.dsl_classes.general_settings import GeneralSettings


def parse_dsl(dsl_path, game_path):
    # Load the metamodel from the DSL grammar
    this_folder = dirname(__file__)
    # dsl_mm = metamodel_from_file(join(this_folder, "gameDSL.tx"))
    dsl_mm = metamodel_from_file(join(this_folder, dsl_path))

    # Parse the DSL file and create the GameWorld
    model = dsl_mm.model_from_file(join("games\\" + game_path, game_path))
    # model = dsl_mm.model_from_file(join(this_folder, "generatedGame.game"))
    # model = dsl_mm.model_from_file(join(this_folder, "testGame.game"))

    game_world = GameWorld()

    # Create regions
    for region_def in model.regions:
        region = Region(region_def.name, region_def.portrayal)
        for connection in region_def.connections:
            region.add_connection(connection.direction, connection.target)
        for requirement in region_def.requirements:
            region.add_requirements(requirement.item)
        if region_def.environmental_dmg:
            region.add_environmental_dmg(region_def.environmental_dmg.amount)
        for item in region_def.contains:
            temp_item = item
            if type(item)._tx_fqn == 'gameDSL.Item':
                temp_activations = []
                item_to_save = Item(item.name, item.portrayal, item.isStatic)
                for activation in item.activations:
                    action_name = activation.action.__class__.__name__
                    if action_name == "RestoreHealthAction":
                        temp_activations.append(HealAction(activation.action.amount))
                    elif action_name == "RestoreManaAction":
                        temp_activations.append(RestoreManaAction(activation.action.amount))
                item_to_save.activations = temp_activations
                temp_item = item_to_save
            elif type(item)._tx_fqn == 'gameDSL.Weapon':
                corrected_modefiers = []
                weapon_to_save = Weapon(
                        item.name,
                        item.portrayal,
                        item.type,
                        item.healthDamage,
                        item.manaDamage,
                        item.healthCost,
                        item.manaCost,
                        item.requiredLevel
                    )
                for modefier in item.modifiers:
                    corrected_modefiers.append({'coefficients': modefier.coefficients,
                                                'modifiableAttribute': modefier.modifiableAttribute})
                weapon_to_save.modifiers = corrected_modefiers
                temp_item = weapon_to_save

            elif type(item)._tx_fqn == 'gameDSL.Armor':
                corrected_modefiers = []
                armor_to_save = Armor(
                        item.name,
                        item.portrayal,
                        item.type,
                        item.defense,
                        item.manaDefense,
                        item.requiredLevel
                    )
                for modefier in item.modifiers:
                    corrected_modefiers.append({'coefficients': modefier.coefficients,
                                                'modifiableAttribute': modefier.modifiableAttribute})
                armor_to_save.modifiers = corrected_modefiers
                temp_item = armor_to_save

            region.add_item(temp_item)
        game_world.regions.append(region)

    # Create items
    for item_def in model.items:
        item = Item(item_def.name, item_def.portrayal, item_def.isStatic)
        item.contains = [item.name for item in item_def.contains]
        item.activations = []
        for activation in item_def.activations:
            action_name = activation.action.__class__.__name__
            if action_name == "RestoreHealthAction":
                item.activations.append(HealAction(activation.action.amount))
            elif action_name == "RestoreManaAction":
                item.activations.append(RestoreManaAction(activation.action.amount))
        game_world.items[item.name] = item

    # Create weapons
    for weapon_def in model.weapons:
        weapon = Weapon(
            weapon_def.name,
            weapon_def.portrayal,
            weapon_def.type,
            weapon_def.healthDamage,
            weapon_def.manaDamage,
            weapon_def.healthCost,
            weapon_def.manaCost,
            weapon_def.requiredLevel
        )
        modifiers = weapon_def.modifiers
        for modifier in modifiers:
            weapon.add_modifier(modifier.modifiableAttribute, modifier.coefficients)
        game_world.weapons[weapon_def.name] = weapon

    # Create armors
    for armor_def in model.armors:
        armor = Armor(
            armor_def.name,
            armor_def.portrayal,
            armor_def.type,
            armor_def.defense,
            armor_def.manaDefense,
            armor_def.requiredLevel
        )
        modifiers = armor_def.modifiers
        for modifier in modifiers:
            armor.add_modifier(modifier.modifiableAttribute, modifier.coefficients)
        game_world.armors[armor_def.name] = armor

    # Create player
    player_def = model.player

    initial_position = None
    for region in game_world.regions:
        if region.name == player_def.position.name:
            initial_position = region
            break
    player = Player(player_def.name, initial_position, player_def.vigor, player_def.endurance, player_def.strength,
                    player_def.intelligence,
                    player_def.health, player_def.mana, player_def.damage, player_def.defence, player_def.manaDamage,
                    player_def.manaDefence)

    player.current_experience = player_def.currentExperience
    player.needed_experience_for_level_up = player_def.neededExperienceForLevelUp
    player.levelScalingPercentage = player_def.levelScalingPercentage
    player.level = player_def.level
    player.inventory = [item.name for item in player_def.inventory]
    player.can_equip = player_def.canEquip
    game_world.player = player

    # Create enemies
    for enemy_def in model.enemies:
        enemy_initial_position = None
        for region in game_world.regions:
            if region.name == enemy_def.position.name:
                enemy_initial_position = region

        enemy = Enemy(enemy_def.name.replace("_", " "), enemy_def.portrayal, enemy_initial_position, enemy_def.health,
                      enemy_def.mana, enemy_def.xp)
        for attack in enemy_def.attackTypes:
            enemy.attacks.append({
                'name': attack.name,
                'health_damage': attack.healthDamage,
                'health_damage_variance': attack.healthDamageVariance,
                'mana_damage': attack.manaDamage,
                'mana_damage_variance': attack.manaDamageVariance,
                'health_cost': attack.healthCost,
                'mana_cost': attack.manaCost,
                'frequency': attack.frequency
            })
        enemy.healing_chance = enemy_def.healingChance
        enemy.healing_amount = enemy_def.healingAmount
        enemy.healing_amount_variance = enemy_def.healingAmountVariance
        for item in enemy_def.inventory:
            try:
                if type(item)._tx_fqn == 'gameDSL.Item':
                    temp_activations = []
                    item_to_save = Item(item.name, item.portrayal, item.isStatic)
                    for activation in item.activations:
                        action_name = activation.action.__class__.__name__
                        if action_name == "RestoreHealthAction":
                            temp_activations.append(HealAction(activation.action.amount))
                        elif action_name == "RestoreManaAction":
                            temp_activations.append(RestoreManaAction(activation.action.amount))
                    item_to_save.activations = temp_activations
                    item = item_to_save
                elif type(item)._tx_fqn == 'gameDSL.Weapon':
                    corrected_modefiers = []
                    weapon_to_save = Weapon(
                        item.name,
                        item.portrayal,
                        item.type,
                        item.healthDamage,
                        item.manaDamage,
                        item.healthCost,
                        item.manaCost,
                        item.requiredLevel
                    )
                    for modefier in item.modifiers:
                        corrected_modefiers.append({'coefficients': modefier.coefficients,
                                                    'modifiableAttribute': modefier.modifiableAttribute})
                    weapon_to_save.modifiers = corrected_modefiers
                    item = weapon_to_save

                elif type(item)._tx_fqn == 'gameDSL.Armor':
                    corrected_modefiers = []
                    armor_to_save = Armor(
                        item.name,
                        item.portrayal,
                        item.type,
                        item.defense,
                        item.manaDefense,
                        item.requiredLevel
                    )
                    for modefier in item.modifiers:
                        corrected_modefiers.append({'coefficients': modefier.coefficients,
                                                    'modifiableAttribute': modefier.modifiableAttribute})
                    armor_to_save.modifiers = corrected_modefiers
                    item = armor_to_save
            except:
                pass
            enemy.items_to_drop[item.name] = item
        game_world.enemies.append(enemy)

    # Set start and final positions
    for player_region in game_world.regions:
        if player_region.name == model.start_position.name:
            game_world.set_start_position(player_region)
        elif player_region.name == model.final_position.name:
            game_world.set_final_position(player_region)

    # Set settings
    for settings_def in model.settings:
        settings = GeneralSettings(settings_def.dropOtherWeapons, settings_def.dropOtherArmors,
                                   settings_def.additionalTurnAfterUse)
        game_world.settings = settings

    return game_world
