import random
import json


# Utility Functions
def save_to_json(game_data):
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(game_data, f, indent = 4, ensure_ascii = False)


def validate(options, message):
    value = ""

    while value not in options:
        value = str(input(f"{message}").lower())

        if value not in options:
            print("Invalid input\n")

    return value


def dice_roll(max_roll = 20):
    # Roll a random int from 1 to max_roll, 20 if no amount is given
    return random.randint(1, max_roll)


def reset_data(game_data):
    # Assign player data variables
    player_data = game_data.get("PlayerData")
    player_progress = player_data.get("PlayerProgress")

    # Reset player data
    for part in (player_profile := player_data.get("PlayerProfile")).keys():
        player_profile[part] = ""

    for attribute in (player_attributes := player_data.get("PlayerAttributes")).keys():
        player_attributes[attribute] = 0

    for condition in (player_condition := player_data.get("PlayerCondition")).keys():
        player_condition[condition] = 0

    player_data.get("PlayerSkills").clear()

    player_data.get("PlayerInventory").clear()
    player_data.get("PlayerEquipment").clear()

    player_progress = player_data.get("PlayerProgress")
    for part in ("Experience", "MapZone", "DaysPassed"):
        player_progress[part] = 0

    player_progress["MapDimension"] = "Overworld"

    # Add "coins" to inventory since it is a currency
    player_inventory = player_data.get("PlayerInventory")
    player_inventory["coins"] = {
        "Amount": 0,
        "Price": 1
    }

    # Save cleared player inventory
    save_to_json(game_data)


def restart(game_data):
    # Only continue if player has agreed twice
    if str(input("Do you really want to restart? (Y/N)\n> ").upper()) == "Y" and \
       str(input("\nAre you sure? (Y/N)\n> ").upper()) == "Y":
        # Set up new character
        character_setup(game_data)


# Gameplay Functions
def character_setup(game_data):
    # Reset data so there is no save conflict
    reset_data(game_data)

    # Assign player_data and class_data
    player_data = game_data.get("PlayerData")
    player_profile = player_data.get("PlayerProfile")
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")
    player_skills = player_data.get("PlayerSkills")

    class_data = game_data.get("ClassData")

    # Assign name
    player_name = str(input("\nWhat is your characters name?\n> "))
    player_profile["Name"] = player_name

    # Loop until valid player class is chosen
    player_class = validate(
        (classes := class_data.keys()),
        f"\nWhat is your characters class?\n{", ".join(classes)}\n> "
    )

    # Assign class once
    player_profile["Class"] = player_class

    # Assign each attribute based on class
    for attribute in ("Strength", "Dexterity", "Intelligence"):
        player_attributes[attribute] = class_data[player_class][attribute]

    # Assign health and stamina based on class
    for condition in ("Health", "Stamina"):
        player_condition[condition] = class_data[player_class][condition]

    # Assign max health and stamina with slicing
    for condition in ("MaxHealth", "MaxStamina"):
        player_condition[condition] = player_condition[condition[3:]]

    # Add class skills to player_skills
    player_skills.extend(class_data[player_class]["Skills"])

    # Welcome player and display stats
    print(f"\nWelcome {player_name} the {player_class}!\n")

    print(
        f"Your stats are:\n"
        f"Attributes: {", ".join([f"{key}: {value}" for key, value in player_attributes.items()])}\n"
        f"Condition: {", ".join([f"{key}: {value}" for key, value in list(player_condition.items())[::2]])}\n"
        f"Skills: {", ".join([skill.capitalize() for skill in player_skills])}"
    )

    # Update game_data json file
    save_to_json(game_data)


def quit_game(game_data):
    # Update game_data json file
    save_to_json(game_data)

    quit()


def combat(game_data, enemy_class, map_dimension, monster_name):
    # Define enemy statistics based off of arguments
    enemy_data = game_data.get("MonsterData")[map_dimension][enemy_class][monster_name]
    enemy_health = enemy_data.get("Health")
    enemy_damage = enemy_data.get("Damage")

    # Define player statistics
    player_data = game_data.get("PlayerData")
    player_condition = player_data.get("PlayerCondition")
    player_attributes = player_data.get("PlayerAttributes")
    player_equipment = player_data.get("PlayerEquipment")
    player_skills = player_data.get("PlayerSkills")

    current_health = player_condition.get("Health")
    max_health = player_condition.get("MaxHealth")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Set buff counter
    buff_turns = 0

    # Loop combat until either player or enemy dies
    while current_health > 0 and enemy_health > 0:
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
                types = ("melee", "ranged", "spell")
                available_types = [skill for skill in types if skill in player_skills]

                attack_type = validate(
                    available_types,
                    f"How would {player_name} like to attack?\n{", ".join(available_types)}\n> "
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

                enemy_health -= player_damage

                # Limit enemy_health to 0, not -4 for example
                if enemy_health < 0:
                    enemy_health = 0

                print(
                    f"{player_name} did {player_damage} damage!\n"
                    f"The {monster_name} has {enemy_health} HP left."
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

        # Continue fight if enemy still alive
        if enemy_health > 0:
            # Calculate damage dealt by enemy
            damage_dealt = round(
                ((enemy_damage / defence_multiplier) * (dice_roll(20) / 10)),
                0
            )
            current_health -= damage_dealt

            print(
                f"The {monster_name} did {damage_dealt} damage!\n"
                f"{player_name} has {current_health} HP left."
            )

        else:
            # Reward player with experience and coins with maximum of monster XP
            experience_gained = enemy_data.get("Experience", 0)

            print(
                f"{player_name} defeated the {monster_name} "
                f"and gained {experience_gained} XP!\n"
            )

            aquire(game_data, "coins", 100, experience_gained, 1)

            player_progress = player_data.get("PlayerProgress")
            player_progress["Experience"] += experience_gained
            break

    if current_health <= 0:
        print(f"{player_name} has died!")

        # Update game_data json file
        save_to_json(game_data)

        return

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


def adventure(game_data):
    # Assign player data
    player_data = game_data.get("PlayerData")
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")
    player_progress = player_data.get("PlayerProgress")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Stamina cost for adventuring
    stamina_cost = 10

    # Prevent stamina going below 0
    if (player_condition["Stamina"] - stamina_cost) < 0:
        print(
            f"{player_name} doesn't have enough stamina to adventure, "
            f"{player_name} should rest!"
        )
        return

    # Remove stamina from player_condition
    player_condition["Stamina"] -= stamina_cost

    print(f"{player_name} has used {stamina_cost} stamina points to adventure.")

    # Encounter if player intelligence passes sight check
    if player_attributes.get("Intelligence") > dice_roll(20):
        monster_data = game_data.get("MonsterData")

        monster_name = random.choice(
            list(monster_data[player_progress.get("MapDimension")]["Monsters"].keys())
        )

        print(f"{player_name} encountered a {monster_name}")

        combat(
            game_data,
            "Monsters",
            player_progress.get("MapDimension"),
            monster_name
        )
    else:
        print(f"{player_name} encountered nothing.")

    # Increase days_passed
    player_progress["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


def aquire(game_data, item_name, spawn_percentage = 20, max_spawn_amount = 5, item_price = 10):
    # Aquire item with game_data to add item onto, name of item, spawn chance, max spawn amount, and price
    player_data = game_data.get("PlayerData")
    player_inventory = player_data.get("PlayerInventory")

    # Random chance from 1 to spawn_percentage, which accepts that is or is under 1
    if random.uniform(0, 100 / spawn_percentage) <= 1:
        spawn_amount = random.randint(1, max_spawn_amount)

        print(
            f"{player_data.get("PlayerProfile").get("Name")} "
            f"got {spawn_amount} {item_name}!"
        )

        # .get() can give existing amount, or 0 if it doesn't exist yet
        player_inventory[item_name] = {
            "Amount": player_inventory.get(item_name, {}).get("Amount", 0) + spawn_amount,
            "Price": item_price
        }

    # Update game_data json file
    save_to_json(game_data)


def mine(game_data):
    player_data = game_data.get("PlayerData")
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")

    player_name = player_data.get("PlayerProfile").get("Name")

    loot_data = game_data.get("LootData").get("Mine")

    # Stamina cost for mining
    stamina_cost = 10

    # Prevent stamina going below 0
    if (player_condition["Stamina"] - stamina_cost) < 0:
        print(
            f"{player_name} doesn't have enough stamina to mine, "
            f"{player_name} should rest!"
        )
        return

    player_condition["Stamina"] -= stamina_cost

    print(
        f"{player_name} has used {stamina_cost} stamina points to mine, "
        f"and now has {player_condition.get("Stamina")} stamina left."
    )

    # Higher chance on materials if strength is high
    mine_factor = player_attributes.get("Strength") / 10

    # Mining materials which can be found
    for key in loot_data.keys():
        aquire(
            game_data,
            key,
            loot_data[key].get("chance") / mine_factor,
            loot_data[key].get("maxAmount"),
            loot_data[key].get("price")
        )

    # Increase days_passed
    player_data.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


def gather(game_data):
    player_data = game_data.get("PlayerData")
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")

    player_name = player_data.get("PlayerProfile").get("Name")

    loot_data = game_data.get("LootData").get("Forest")

    # Stamina cost for gathering
    stamina_cost = 10

    # Prevent stamina going below 0
    if (player_condition["Stamina"] - stamina_cost) < 0:
        print(
            f"{player_name} doesn't have enough stamina to adventure, "
            f"{player_name} should rest!"
        )
        return

    player_condition["Stamina"] -= stamina_cost

    print(
        f"{player_name} has used {stamina_cost} stamina points to gather, "
        f"and now has {player_condition.get("Stamina")} stamina left."
    )

    # Higher chance on materials if dexterity is high
    gather_factor = player_attributes.get("Dexterity") / 10

    # Forest materials which can be found
    for key in loot_data.keys():
        aquire(
            game_data,
            key,
            loot_data[key].get("chance") / gather_factor,
            loot_data[key].get("maxAmount"),
            loot_data[key].get("price")
        )

    # Increase days_passed
    player_data.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


def rest(game_data):
    # Define player statistics
    player_data = game_data.get("PlayerData")
    player_condition = player_data.get("PlayerCondition")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Define health and stamina
    current_health = player_condition.get("Health")
    max_health = player_condition.get("MaxHealth")

    current_stamina = player_condition.get("Stamina")
    max_stamina = player_condition.get("MaxStamina")

    # Ask player for short or long rest
    action = validate(
        ("long", "short"),
        f"How long would {player_name} like to rest?\nlong, short\n> "
    )

    # Calculate regenerated health and stamina based on rest time
    regenerated_health = (max_health * 1) if action == "long" else (max_health * 0.25)
    regenerated_stamina = (max_stamina * 1) if action == "long" else (max_stamina * 0.5)

    # Limit regenerated_health so current_health will not exceed max_health
    if (current_health + regenerated_health) > max_health:
        regenerated_health = max_health - current_health

    # Limit regenerated_stamina so current_stamina will not exceed max_stamina
    if (current_stamina + regenerated_stamina) > max_stamina:
        regenerated_stamina = max_stamina - current_stamina

    # Add regenerated health and stamina onto current
    current_health += regenerated_health
    current_stamina += regenerated_stamina

    print(
        f"\n{player_name} regenerated {regenerated_health} health.\n"
        f"{player_name} now has {current_health} HP."
        f"{player_name} regained {regenerated_stamina} stamina.\n"
        f"{player_name} now has {current_stamina} stamina."
    )

    # Save player health and stamina
    player_condition["Health"] = current_health
    player_condition["Stamina"] = current_stamina

    # Increase days_passed based on rest length
    player_data.get("PlayerProgress")["DaysPassed"] += 1 if action == "long" else 0.5

    # Update game_data json file
    save_to_json(game_data)


def buy(game_data):
    # Define player data
    player_data = game_data.get("PlayerData")
    player_inventory = player_data.get("PlayerInventory")
    player_equipment = player_data.get("PlayerEquipment")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Define shop items
    shop_data = game_data.get("ShopData")

    # Get input for which item player wants to buy
    item = validate(
        shop_items := list(shop_data.keys()),
        f"What item would {player_name} like to browse?\n"
        f"The shop currently has:\n{", ".join(shop_items)}\n> "
    )

    # Print price of item
    item_price = shop_data.get(item).get("Price")

    print(f"\nThe {item} costs {item_price} coins.")

    buy_confirmation = validate(
        ("y", "n"),
        f"Would {player_name} like to buy the {item}? (Y/N)\n> "
    )

    if buy_confirmation == "y":
        if player_inventory.get("coins", {}).get("Amount") >= item_price:
            aquire(game_data, item, 100, 1, item_price)
            player_inventory["coins"]["Amount"] -= item_price

            # Add item to player_equipment for specific types
            if shop_data.get(item).get("Type") in ["Weapon", "Armour"]:
                player_equipment[item] = {
                    "Type": shop_data.get(item).get("Type")
                }

                if shop_data.get(item).get("Type") == "Weapon":
                    player_equipment[item]["DamageIncrease"] = shop_data.get(item).get("DamageIncrease")
                elif shop_data.get(item).get("Type") == "Armour":
                    player_equipment[item]["DamageNegation"] = shop_data.get(item).get("DamageNegation")

        else:
            print(f"{player_name} doesn't have enough coin.")

    elif buy_confirmation == "n":
        print()
        shop(game_data)

    # Update game_data json file
    save_to_json(game_data)


def sell(game_data):
    # Define player data
    player_data = game_data.get("PlayerData")
    player_inventory = player_data.get("PlayerInventory")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Get input for which item player wants to buy
    item = validate(
        # [1:] so it will exclude coins, and turn to list since you can't slice dict.keys()
        inventory_items := list(player_inventory.keys())[1:],
        f"What item would {player_name} like to sell? "
        f"{player_name} currently has:\n{", ".join(inventory_items)}\n> "
    )

    # Print price of item
    print(
        f"\nThe {item} sells for "
        f"{player_inventory.get(item).get("Price")} coins."
    )

    # Ask for confirmation to sell item
    sell_confirmation = validate(
        ("y", "n"),
        f"Would {player_name} like to sell the {item}? (Y/N)\n> "
    )

    if sell_confirmation == "y":
        if player_inventory.get(item).get("Amount") > 0:
            # Not aquire for coins since coins already exists in json at character creation
            player_inventory["coins"]["Amount"] += player_inventory.get(item).get("Price")
            player_inventory[item]["Amount"] -= 1

            # Remove item from inventory if 0 left
            if player_inventory[item].get("Amount") <= 0:
                player_inventory.pop(item)

        else:
            print(f"{player_name} doesn't have enough {item}.")

    elif sell_confirmation == "n":
        print()
        shop(game_data)

    # Update game_data json file
    save_to_json(game_data)


def shop(game_data):
    action = validate(
        ("buy", "sell", "leave"),
        f"What would {game_data.get("PlayerData").get("PlayerProfile").get("Name")} "
        f"like to do in the shop?\nbuy, sell, leave\n> "
    )

    # Empty line after player action
    print()

    match action:
        case "buy":
            buy(game_data)
        case "sell":
            sell(game_data)
        case "leave":
            return

    # Increase days_passed
    game_data.get("PlayerData").get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


def status(game_data):
    # Assign player data
    player_data = game_data.get("PlayerData")
    player_condition = player_data.get("PlayerCondition")
    player_progress = player_data.get("PlayerProgress")
    player_name = player_data.get("PlayerProfile").get("Name")

    print(f"It is currently day {round(player_progress.get("DaysPassed"), 0)}.")

    print(
        f"{player_name} currently has {player_condition.get("Health")} HP "
        f"and {player_condition.get("Stamina")} stamina."
    )

    print(
        f"{player_name} currently has {player_progress.get("Experience")} XP points, "
        f"and is located in map zone {player_progress.get("MapZone")} "
        f"in the \"{player_progress.get("MapDimension")}.\""
    )


# Main Function
def main():
    with open("data.json", "r", encoding = "utf-8") as f:
        game_data = json.load(f)

    player_data = game_data.get("PlayerData")
    player_profile = player_data.get("PlayerProfile")

    if player_profile.get("Class") == "":
        character_setup(game_data)

    while True:
        # Reassign game_data after each action
        with open("data.json", "r", encoding = "utf-8") as f:
            game_data = json.load(f)

        # Possible actions with game_data as argument
        possible_actions = {
            "quit": quit_game,
            "adventure": adventure,
            "mine": mine,
            "gather": gather,
            "rest": rest,
            "status": status,
            "shop": shop,
            "restart": restart
        }

        action = validate(
            possible_actions,
            f"\nWhat would {game_data.get("PlayerData").get("PlayerProfile").get("Name")} "
            f"like to do?\n{", ".join(list(possible_actions))}\n> "
        )

        # Empty line after player action
        print()

        if action in possible_actions:
            possible_actions[action](game_data)
        else:
            print("Invalid action")


# Call main
if __name__ == "__main__":
    main()