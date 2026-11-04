import random
from utils import validate, save_to_json, dice_roll, get_player_data
from economy import aquire
from combat import combat


# = WORLD FUNCTIONS
# Adventure where character can spot monster
def adventure(game_data, game_content):
    # Assign player data
    player_data = get_player_data(game_data)
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")
    player_progress = player_data.get("PlayerProgress")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Stamina cost for adventuring
    stamina_cost = 10

    # Prevent adventuring if player is dead
    if player_condition["Health"] <= 0:
        print(
            f"{player_name} doesn't have enough health to adventure, "
            f"{player_name} should rest!"
        )
        return

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
        monster_data = game_content.get("MonsterData")

        # Encounter as many monsters as players level is
        monster_amount = player_progress.get("Level")

        # Chose monster_amount random monster names
        monsters = [random.choice(list(monster_data[player_progress.get("MapDimension")]
                                  ["Monsters"].keys())) for _ in range(monster_amount)]

        # Print what player found, grammatically correct
        print(
            f"{player_name} encountered "
            f"{", ".join([f"a {monster_name}" for monster_name in monsters[:-1]]) +
               f" and " if len(monsters) > 1 else ""}"
            f"a {monsters[-1]}!"
        )

        # Start combat with multiple monsters
        combat(
            game_data,
            game_content,
            "Monsters",
            player_progress.get("MapDimension"),
            monsters
        )
    else:
        print(f"{player_name} encountered nothing.")

    # Increase days_passed
    player_progress["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


# Mine to aquire gemstones
def mine(game_data, game_content):
    player_data = get_player_data(game_data)
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")

    player_name = player_data.get("PlayerProfile").get("Name")

    loot_data = game_content.get("LootData").get("Mine")

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
            loot_data[key].get("Spawn Chance") / mine_factor,
            loot_data[key].get("Max Spawn Amount"),
            game_content.get("ItemData").get(key).get("Price")
        )

    # Increase days_passed
    player_data.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


# Forage to find loot
def gather(game_data, game_content):
    player_data = get_player_data(game_data)
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")

    player_name = player_data.get("PlayerProfile").get("Name")

    loot_data = game_content.get("LootData").get("Forest")

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
            loot_data[key].get("Spawn Chance") / gather_factor,
            loot_data[key].get("Max Spawn Amount"),
            game_content.get("ItemData").get(key).get("Price")
        )

    # Increase days_passed
    player_data.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


# Rest to regain stamina and health
def rest(game_data):
    # Define player statistics
    player_data = get_player_data(game_data)
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
        f"{player_name} now has {current_health} HP.\n"
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
