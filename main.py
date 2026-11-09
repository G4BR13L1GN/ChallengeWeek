import player
from economy import shop, crafting
from world import adventure, mine, gather, rest
from utils import validate, quit_game, load_from_json, get_save_data


# Things to add:
# 1. Improve choice system:

#   Choice 1
# > Choice 2
#   Choice 3

# 2. Text revealing on screen letter per letter

# 3. Game tutorial (maybe questions and answers)


# Main Function
def main():
    while True:
        # Reassign save_data after each action to get new updated version
        save_data, game_data = load_from_json("save_data", "game_data")

        # Check if player class not empty (character not set up yet)
        player_data = get_save_data(save_data)
        player_profile = player_data.get("PlayerProfile")

        # Check if character save is empty
        if player_profile.get("Class") == "":
            # Fully reset all data to make sure character is blank
            player.reset_data(save_data)

            # Set up new character
            player.character_setup(save_data, game_data)

        # Reassign player_data, might have changed if character was not set up
        player_data = get_save_data(save_data)

        # Checks if character leveled up
        player.check_for_level_up(save_data)

        # Possible actions with save_data as argument
        possible_actions = {
            "quit": lambda: quit_game(save_data),
            "adventure": lambda: adventure(save_data, game_data),
            "mine": lambda: mine(save_data, game_data),
            "gather": lambda: gather(save_data, game_data),
            "rest": lambda: rest(save_data),
            "status": lambda: player.status(save_data),
            "shop": lambda: shop(save_data, game_data),
            "crafting": lambda: crafting(save_data, game_data),
            "restart": lambda: player.restart(save_data, game_data),
            "switch character": lambda: player.switch_character(save_data)
        }

        # Validate actions with options being possible actions
        action = validate(
            (possible_actions.keys()),
            f"\nWhat would {player_data.get("PlayerProfile").get("Name")} "
            f"like to do?\n"
            f"adventure, mine, gather\n"
            f"rest, status, shop, crafting\n"
            f"quit, switch character, restart\n> "
        )

        # Empty line after player action
        print()

        possible_actions[action]()


# Call main
if __name__ == "__main__":
    main()
