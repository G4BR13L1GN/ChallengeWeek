import random
import json


# = UTILITY FUNCTIONS
# Save data to json
def save_to_json(game_data):
    # Open json file and dump game_data into the file
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(game_data, f, indent=4, ensure_ascii=False)


# Ask input until user input in valid options
def validate(options, message, data_type=str):
    user_input = ""

    # Loop until valid
    while user_input not in options:
        user_input = input(message).lower()

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
