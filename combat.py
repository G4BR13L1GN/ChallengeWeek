import random
from utils import validate, save_to_json, dice_roll, get_player_data
from economy import add_item


# = COMBAT FUNCTIONS
class Enemy:
    def __init__(self, name, data):
        self.data = data
        self.name = name
        self.health = data.get("Health")
        self.damage = data.get("Damage")

    def __repr__(self):
        return f"Enemy: ('{self.name}', {self.health}, {self.damage})"


def combat(save_data, game_data, enemy_class, map_dimension, enemy_names):
    # Define enemy statistics based off of arguments
    enemies = []

    # Make enemy using class for each enemy name in enemy_names
    for enemy in enemy_names:
        monster_data = game_data.get("MonsterData")[map_dimension][enemy_class][enemy]
        new_monster = Enemy(enemy, monster_data)
        enemies.append(new_monster)

    # Define player statistics
    player_data = get_player_data(save_data)
    player_condition = player_data.get("PlayerCondition")
    player_attributes = player_data.get("PlayerAttributes")
    player_equipment = player_data.get("PlayerEquipment")
    player_skills = player_data.get("PlayerSkills")

    current_health = player_condition.get("Health")
    max_health = player_condition.get("MaxHealth")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Set buff counter
    buff_turns = 0

    # Loop combat until either player or all enemies dead
    while current_health > 0 and any(enemy.health > 0 for enemy in enemies):
        # Repeat loop if action is not in player_skills
        action = validate(
            ("attack", "defence", "support"),
            f"\nWhat would {player_name} like to do?\nattack, defence, support\n> "
        )

        # Empty line after checking attack
        print()

        # Assign attack and defence multiplier
        attack_multiplier, defence_multiplier = 1, 1

        # Change attack and defence multiplier based on highest armour rating
        for key in player_equipment.keys():
            equipment = player_equipment.get(key)

            if equipment.get("Type") == "Weapon":
                if equipment.get("DamageIncrease") > attack_multiplier:
                    attack_multiplier = equipment.get("DamageIncrease")
            elif equipment.get("Type") == "Armour":
                if equipment.get("DamageNegation") > defence_multiplier:
                    defence_multiplier = equipment.get("DamageNegation")

        # Apply / remove buff
        attack_multiplier *= 1.2 if buff_turns > 0 else 1
        defence_multiplier *= 1.2 if buff_turns > 0 else 1

        # Remove buff counter
        buff_turns -= 1 if buff_turns > 0 else 0

        # Different functions based on action
        match action:
            case "attack":
                # Ask which enemy player would like to attack
                enemy_to_attack = validate(
                    [enemy.name for enemy in enemies],
                    f"\nWhich enemy would {player_name} like to attack?\n"
                    f"{", ".join([enemy.name for enemy in enemies])}\n> "
                )

                # Get first iteration of enemy where name is same as enemy_to_attack
                # (If there are 2 bandits, this will choose first one)
                enemy = next(e for e in enemies if e.name == enemy_to_attack)

                # Player can choose attack type if in player_skills
                types = ("melee", "ranged", "spell")
                available_types = [skill for skill in types if skill in player_skills]

                attack_type = validate(
                    available_types,
                    f"\nHow would {player_name} like to attack?\n{", ".join(available_types)}\n> "
                )

                player_damage = 0

                match attack_type:
                    # Deal damage based on attributes, from 0.1 to 2.0x damage
                    case "melee":
                        player_damage = round(
                            ((player_attributes.get("Strength") * (dice_roll(20) / 10)) * attack_multiplier),
                            0
                        )
                    case "ranged":
                        player_damage = round(
                            ((player_attributes.get("Dexterity") * (dice_roll(20) / 10)) * attack_multiplier),
                            0
                        )
                    case "spell":
                        player_damage = round(
                            ((player_attributes.get("Intelligence") * (dice_roll(20) / 10)) * attack_multiplier),
                            0
                        )

                enemy.health -= player_damage

                # Limit enemy.health to 0, not -4 for example
                if enemy.health < 0:
                    enemy.health = 0

                print(
                    f"\n{player_name} did {player_damage} damage!\n"
                    f"The {enemy.name} has {enemy.health} HP left."
                )

            case "defence":
                types = ("block", "dodge", "ward")
                available_types = [skill for skill in types if skill in player_skills]

                defend_type = validate(
                    available_types,
                    f"How would {player_name} like to defend?\n{", ".join(available_types)}\n> "
                )

                dice_roll_result = dice_roll(20)

                match defend_type:
                    case "block":
                        # Double defence_multiplier if strength * roll > 10
                        defence_multiplier *= 2 if (
                            player_attributes.get("Strength") * (dice_roll_result / 10)
                        ) > 10 else 1

                    case "dodge":
                        # Double defence_multiplier if dexterity * roll > 10
                        defence_multiplier *= 2 if (
                            player_attributes.get("Dexterity") * (dice_roll_result / 10)
                        ) > 10 else 1

                    case "ward":
                        # Double defence_multiplier if intelligence * roll > 10
                        defence_multiplier *= 2 if (
                            player_attributes.get("Intelligence") * (dice_roll_result / 10)
                        ) > 10 else 1

                print(
                    f"{player_name} performed a succesful block, damage negation * 2 for this turn!"
                    if dice_roll_result > 10
                    else f"{player_name} failed the defence action, no damage negation bonus this turn!"
                )

            case "support":
                types = ("buff", "heal")  # add warcry, focus, concentrate instead of general buff
                available_types = [skill for skill in types if skill in player_skills]

                support_type = validate(
                    available_types,
                    f"How would {player_name} like to defend?\n{", ".join(available_types)}\n> "
                )

                match support_type:
                    case "buff":
                        buff_turns = 3
                        print(
                            f"{player_name} applied buff, weapon damage and damage negation * 1.2!"
                        )

                    case "heal":
                        # Heal 10 to 30 HP
                        regenerated_health = 10 + dice_roll(20)

                        # Limit regenerated_health so current_health will not exceed max_health
                        if (current_health + regenerated_health) > max_health:
                            regenerated_health = max_health - current_health

                        # Apply healing
                        current_health += regenerated_health

                        print(
                            f"{player_name} healed {regenerated_health} HP!\n"
                            f"{player_name} has {current_health} HP left."
                        )

        # Empty line after player action
        print()

        # Action for each enemy in enemies
        for enemy in enemies:
            # Continue fight if enemy still alive
            if enemy.health > 0:
                # Calculate damage dealt by enemy
                damage_dealt = round(
                    ((enemy.damage / defence_multiplier) * (dice_roll(20) / 10)),
                    0
                )
                current_health -= damage_dealt

                # Return if player died
                if current_health <= 0:
                    print(f"{player_name} has died!")

                    # Update save_data json file
                    save_to_json(save_data)

                    return

                print(
                    f"\nThe {enemy.name} did {damage_dealt} damage!\n"
                    f"{player_name} has {current_health} HP left."
                )

            #
            else:
                # Reward player with experience and coins with maximum of enemy XP
                experience_gained = enemy.data.get("Experience", 0)

                print(
                    f"\n{player_name} defeated the {enemy.name} "
                    f"and gained {experience_gained} XP!\n"
                )

                # Reward player with coins
                add_item(save_data, "coins", experience_gained, 1)

                player_progress = player_data.get("PlayerProgress")
                player_progress["Experience"] += experience_gained
                break

    # Save player health after battle
    player_condition["Health"] = current_health

    # Increase player zone
    print(f"{player_name} has advanced to next map zone!")
    player_progress["MapZone"] += 1

    # Increase days_passed
    player_progress["DaysPassed"] += 0.5

    zones = ("Overworld", "Caverns", "Sift")
    player_progress["MapDimension"] = zones[(player_progress.get("MapZone") - 1) // 6]

    # Update save_data json file
    save_to_json(save_data)
