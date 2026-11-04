from utils import validate, save_to_json, get_player_data


# = PLAYER FUNCTIONS
# Reset all player data
def reset_data(game_data):
    # Assign player data variables
    player_data = get_player_data(game_data)

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

    player_progress["Level"] = 1

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
def restart(game_data, game_content):
    player_data = game_data.get("PlayerData")

    # Ask if player wants to restart current or all characters
    restart_all = validate(
        ("current", "all"),
        "Do you want to restart current character or all?\n"
        "current, all\n> ",
        str
    )

    # Only continue if player has agreed twice
    if str(input("\nDo you really want to restart? (Y/N)\n> ").upper()) == "Y" and \
       str(input("\nAre you sure? (Y/N)\n> ").upper()) == "Y":
        # Set up new character
        if (restart_all):
            # Reset all character
            for char_id in range(1, 4):
                # Get name of character
                char_name = player_data.get(f"P0{char_id}").get("PlayerProfile").get("Name")

                # Switch to character
                switch_character(game_data, char_name)

                # Restart character
                reset_data(game_data)

            # Switch back to first character and setup new character
            switch_character(game_data, "")
            character_setup(game_data, game_content)
        else:
            # Reset current character
            reset_data(game_data)
            character_setup(game_data, game_content)


# Create character for player by choices from player
def character_setup(game_data, game_content):
    # Assign player_data and class_data
    player_data = get_player_data(game_data)

    player_profile = player_data.get("PlayerProfile")
    player_attributes = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")
    player_skills = player_data.get("PlayerSkills")

    class_data = game_content.get("ClassData")

    # Assign name, atleast 2 chars
    player_name = ""

    while True:
        player_name = str(input("\nWhat is your characters name?\n> "))

        if len(player_name) < 2:
            print("Name must be atleast 2 characters long.")
            continue

        break

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
        f"Attributes: {", ".join([f"{key}: {value}" for key,
                                 value in player_attributes.items()])}\n"
        f"Condition: {", ".join([f"{key}: {value}" for key, value in list(
            player_condition.items())[::2]])}\n"
        f"Skills: {", ".join([skill.capitalize() for skill in player_skills])}"
    )

    # Update game_data json file
    save_to_json(game_data)


# Switch character saves
def switch_character(game_data, char_name="NONE CHOSEN"):
    # List of dictionaries for each character
    character_dicts = list(game_data.get("PlayerData").items())[1:]

    # List of all names from characters dict, to lower case
    names_list = list(map(lambda name: name.lower(), list(
        [list(char[1].values())[0]["Name"] for char in character_dicts])))

    # Set ids for names shorter than 2 characters (nonexistent characters because names are atleast 2 chars)
    for name in names_list:
        if len(name) < 2:
            name_index = names_list.index(name)
            names_list[name_index] = f"p0{name_index + 1} (character save empty)"

    # Dict with names linked to id ({"p01": name, ...})
    id_names = list(zip(("p01", "p02", "p03"), names_list))

    # Change selected save based on given argument char_name, else tuple with 3 player ids
    selected_name = char_name.lower() if char_name != "NONE CHOSEN" else validate(
        # Remove " (character save empty)" from actual name
        tuple([part[1].replace(" (character save empty)", "") for part in id_names]),
        f"What character would you like to switch to?\n{", ".join(names_list)}\n> ",
        str
    )

    # Update selected save id
    game_data["PlayerData"]["SelectedSave"] = next(
        (id for id, name in id_names if name == selected_name), "P01").title()

    # Update game_data json file
    save_to_json(game_data)


# Get status of player (heath, stamina, day count)
def status(game_data):
    # Assign player data
    player_data = get_player_data(game_data)
    player_condition = player_data.get("PlayerCondition")
    player_progress = player_data.get("PlayerProgress")
    player_name = player_data.get("PlayerProfile").get("Name")

    print(
        f"It is currently day {round(player_progress.get("DaysPassed"), 0)}.")

    print(
        f"{player_name} currently has {player_condition.get("Health")} HP "
        f"and {player_condition.get("Stamina")} stamina."
    )

    print(
        f"{player_name} currently has {player_progress.get("Experience")} XP points, "
        f"and is located in map zone {player_progress.get("MapZone")} "
        f"in the \"{player_progress.get("MapDimension")}.\""
    )


def check_for_level_up(game_data):
    # Assign player data
    player_data = get_player_data(game_data)
    player_progress = player_data.get("PlayerProgress")
    player_stats = player_data.get("PlayerAttributes")
    player_condition = player_data.get("PlayerCondition")

    while True:
        xp_needed = 100 * player_progress["Level"]

        # Checks if character leveled up
        if player_progress["Experience"] >= xp_needed:
            # Reset experience and add level
            player_progress["Experience"] -= xp_needed
            player_progress["Level"] += 1

            # Increase player condition stats
            player_condition["MaxHealth"] += 10

            # Increase player attributes
            player_stats["Strength"] += 1
            player_stats["Dexterity"] += 1
            player_stats["Intelligence"] += 1

            # Congratulate player
            print(f"Congratulations! You have leveled up to level {player_progress["Level"]}!")
        else:
            break

    # Update game_data json file
    save_to_json(game_data)
