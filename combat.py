import random
from utils import validate, save_to_json, dice_roll
from economy import aquire


class Enemy:
    def __init__(self, name, data):
        self.data = data
        self.name = name
        self.health = data.get("Health")
        self.damage = data.get("Damage")

    def __repr__(self):
        return f"Enemy: ('{self.name}', {self.health}, {self.damage})"


# Special attacks for both player and enemies
def special_attacks(game_data, trigger, player_state):
    # Get player statistics
    player_data = game_data["PlayerData"]
    player_condition = player_data["PlayerCondition"]
    player_inventory = player_data["PlayerInventory"]

    enemy_data = player_state["enemy_data"]
    enemy_effect_data = enemy_data.get(
        "SpecialEffect", enemy_data.get("SpecialEffect", {})
    )

    # Player Equipment Special Effect
    if trigger == "Player Attack":
        for equipment in player_data["PlayerEquipment"].values():
            special_effect = equipment.get("SpecialEffect", {})

            # Reaper Scythe: Life Steal
            if special_effect.get("effect") == "life_steal":
                healing = round(
                    player_state["damage"] * special_effect.get("percentage", 0)
                )
                old_health = player_state["current_health"]

                player_state["current_health"] = min(
                    player_condition["MaxHealth"],
                    old_health + healing
                )

                print(
                    f"Life Steal healed "
                    f"{player_state['current_health'] - old_health} HP!"
                )

    # Enemy special attacks
    if trigger == "enemy_turn":
        if random.random() > enemy_effect_data.get("chance", 0):
            return

        effect = enemy_effect_data.get("effect")

        match effect:
            case "steal_coins":
                # Get player coin amount
                player_coins = player_inventory["coins"]["Amount"]

                # Steal coins, limit to 0 if coins < 0
                stolen = min(player_coins, enemy_effect_data.get("amount", 0))
                player_inventory["coins"]["Amount"] -= stolen

                print(
                    f"The {player_state['monster_name']} stole {stolen} coins!"
                )

            case "stun":
                player_state["stunned"] = enemy_effect_data.get("turns", 1)
                player_state["extra_damage"] += enemy_effect_data.get("damage", 0)

            case "poison" | "bleed" | "burn":
                player_state["damage_over_time"] = enemy_effect_data.get(
                    f"{effect}_damage", 0
                )
                player_state["damage_over_time_turns"] = enemy_effect_data.get(
                    f"{effect}_turns",
                    enemy_effect_data.get("turns", 0)
                )

            case "rage":
                player_state["enemy_damage"] += enemy_effect_data.get(
                    "damage_increase", 0
                )

            case "invisibility":
                player_state["invisible"] = enemy_effect_data.get("turns", 0)

            case "curse":
                player_state["curse_turns"] = enemy_effect_data.get("turns", 0)
                player_state["curse_reduction"] = (
                    enemy_effect_data.get("damage_reduction", 0) / 100
                )

            case "meditate":
                healing = round(
                    player_state["enemy_health"] *
                    enemy_effect_data.get("heal_percentage", 0)
                )

                player_state["enemy_health"] = min(
                    enemy_data["Health"],
                    player_state["enemy_health"] + healing
                )

                player_state["enemy_defence"] = 1 + enemy_effect_data.get(
                    "damage_taken_reduction", 0
                )

                player_state["player_damage_increase"] = enemy_effect_data.get(
                    "player_damage_taken_increase", 0
                )

                player_state["buff_turns"] = enemy_effect_data.get("buff_turns", 0)

            case "shield_wall":
                player_state["enemy_defence"] = 1 + enemy_effect_data.get(
                    "damage_reduction", 0
                )
                player_state["buff_turns"] = enemy_effect_data.get("turns", 0)

            case "darkness":
                player_state["darkness_turns"] = enemy_effect_data.get("turns", 0)
                player_state["accuracy_reduction"] = enemy_effect_data.get(
                    "accuracy_reduction", 50
                )

            case "doom":
                player_state["doom_turns"] = enemy_effect_data.get("turns", 0)
                player_state["doom_percentage"] = enemy_effect_data.get(
                    "damage_percentage", 0
                )

            case "goodbye":
                player_state["current_health"] = 0

    # Damage over time
    if trigger == "player_turn_start":
        if player_state["damage_over_time_turns"] > 0:
            damage = player_state["damage_over_time"]
            player_state["current_health"] -= damage
            player_state["damage_over_time_turns"] -= 1

            print(
                f"You received {damage} damage from a status effect!"
            )

        if player_state["doom_turns"] > 0:
            player_state["doom_turns"] -= 1

            if player_state["doom_turns"] == 0:
                damage = round(
                    player_condition["MaxHealth"] *
                    player_state["doom_percentage"]
                )

                player_state["current_health"] -= damage
                print(f"DOOM dealt {damage} damage!")


def combat(game_data, enemy_class, map_dimension, enemy_names):
    # Define enemy statistics based off of arguments
    enemies = []

    # Make enemy using class for each enemy name in enemy_names
    for enemy in enemy_names:
        monster_data = game_data.get("MonsterData")[map_dimension][enemy_class][enemy]
        new_monster = Enemy(enemy, monster_data)
        enemies.append(new_monster)

    # Define player statistics
    player_data = game_data.get("PlayerData")
    player_condition = player_data.get("PlayerCondition")
    player_attributes = player_data.get("PlayerAttributes")
    player_equipment = player_data.get("PlayerEquipment")
    player_skills = player_data.get("PlayerSkills")

    current_health = player_condition.get("Health")
    max_health = player_condition.get("MaxHealth")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Enemy buff: rage, invisibility, revive, summon, meditate, shield_wall,

    # Set player state
    state = {
        "current_health": current_health,
        "enemy_health": enemy_health,
        "enemy_data": enemy_data,
        "monster_name": monster_name,
        "enemy_damage": enemy_damage,
        "enemy_defence": 1,
        "player_damage_increase": 1,
        "darkness_turns": 0,
        "accuracy_reduction": 50,
        "damage": 0,
        "damage_over_time": 0,
        "damage_over_time_turns": 0,
        "doom_turns": 0,
        "doom_percentage": 0,
        "stunned": 0,
        "extra_damage": 0,
        "invisible": 0,
        "curse_turns": 0,
        "curse_reduction": 0,
        "buff_turns": 0
    }

    # Loop combat until either player or all enemies dead
    while current_health > 0 and [enemy.health > 0 for enemy in enemies]:
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
        buff_turns = player_state["Buffs"]["buff_turns"]
        attack_multiplier *= 1.2 if buff_turns > 0 else 1
        defence_multiplier *= 1.2 if buff_turns > 0 else 1

        # Remove buff counter
        player_state["Buffs"]["buff_turns"] -= 1 if buff_turns > 0 else 0

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

                        # EFFECT: DARKNESS
                        # Darkness can cause player to whiff attack
                        if player_state["darkness_turns"] > 0:
                            if random.random() < player_state["accuracy_reduction"] / 100:
                                player_damage = 0
                                print("The darkness caused your attack to miss!")

                            state["darkness_turns"] -= 1

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
                        player_state["Buffs"]["buff_turns"] = 3
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

                    # Update game_data json file
                    save_to_json(game_data)

                    return

                print(
                    f"\nThe {enemy.name} did {damage_dealt} damage!\n"
                    f"{player_name} has {current_health} HP left."
                )

            else:
                # Reward player with experience and coins with maximum of enemy XP
                experience_gained = enemy.data.get("Experience", 0)

                print(
                    f"\n{player_name} defeated the {enemy.name} "
                    f"and gained {experience_gained} XP!\n"
                )

                aquire(game_data, "coins", 100, experience_gained, 1)

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

    # zones = ["Overworld", "Caverns", "Sift"]
    # player_progress["MapDimension"] = zones[(player_progress.get("MapZone") - 1) // 6]

    # Update game_data json file
    save_to_json(game_data)
