import random
import json


# = UTILITY FUNCTIONS
# Save data to json
def save_to_json(save_data):
    # Open json file and dump game_data into the file
    with open("save_data.json", "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4, ensure_ascii=False)


def load_from_json(*files):
    data_list = []

    for file in files:
        with open(f"{file}.json", "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

            data_list.append(loaded_data)

    return data_list


# Ask input until user input in valid options
def validate(options: tuple, message, data_type=str):
    user_input = ""

    # Loop until valid
    while user_input not in options:
        # Strip and lower player input
        user_input = input(message).strip().lower()

        # Try to convert value, give error if not able to
        try:
            user_input = data_type(user_input)
        except (ValueError, TypeError):
            print("Invalid input, wrong data type\n")
            continue

        # user input not in available options
        if user_input not in options:
            print("Invalid input, not in available options\n")

    # Return valid user input
    return user_input


# Roll dice from 1 to max roll, 20 if no amount is given
def dice_roll(max_roll=20):
    return random.randint(1, max_roll)


# Return player data based on selected save
def get_save_data(save_data, set_id="P00"):
    # Assign player data
    players_data = save_data.get("PlayerData")

    # Get id from function argument, else "SelectedSave", and 1 if not found
    selected_id = players_data.get("SelectedSave", "P00") if set_id == "P00" else set_id

    # Assign player_data and class_data
    player_data = players_data.get(selected_id, {"Message": "Emtpy :("})

    if player_data == {"Message": "Emtpy :("}:
        print("PLAYER NOT FOUND, QUITTING")
        quit()

    return player_data


# Save and quit the game
def quit_game(save_data):
    # Update save_data json file
    save_to_json(save_data)

    # Quit game
    quit()
