from utils import validate, save_to_json


# Reset all player data
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


# Ask for confirmation to reset
def restart(game_data):
    # Only continue if player has agreed twice
    if str(input("Do you really want to restart? (Y/N)\n> ").upper()) == "Y" and \
       str(input("\nAre you sure? (Y/N)\n> ").upper()) == "Y":
        # Set up new character
        character_setup(game_data)


# Create character for player by choices from player
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
    print(
        f"\nWelcome {player_name} the {player_class}!\n"
        f"Your stats are:\n"
        f"Attributes: {", ".join([f"{key}: {value}" for key, value in player_attributes.items()])}\n"
        f"Condition: {", ".join([f"{key}: {value}" for key, value in list(player_condition.items())[::2]])}\n"
        f"Skills: {", ".join([skill.capitalize() for skill in player_skills])}"
    )

    # Update game_data json file
    save_to_json(game_data)


# Save and quit the game
def quit_game(game_data):
    # Update game_data json file
    save_to_json(game_data)

    # Quit game
    quit()


# Get status of player (heath, stamina, day count)
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
