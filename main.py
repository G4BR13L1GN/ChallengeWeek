import json
import player
from economy import shop, crafting
from world import adventure, mine, gather, rest
from utils import validate, quit_game


# Main Function
def main():
    while True:
        # Reassign game_data after each action to get new updated version
        with open("data.json", "r", encoding="utf-8") as f:
            game_data = json.load(f)

        with open("content.json", "r", encoding="utf-8") as f:
            game_content = json.load(f)

        # Check if player class not empty (character not set up yet)
        player_data = player.get_player_data(game_data)

        player_profile = player_data.get("PlayerProfile")

        if player_profile.get("Class") == "":
            # Fully reset all data to make sure character is blank
            player.reset_data(game_data)

            # Set up new character
            player.character_setup(game_data, game_content)

        # Reassign player_data, might have changed if character was not set up
        player_data = player.get_player_data(game_data)

        # Checks if character leveled up
        player.check_for_level_up(game_data)

        # Possible actions with game_data as argument
        possible_actions = {
            "quit": lambda: quit_game(game_data),
            "adventure": lambda: adventure(game_data, game_content),
            "mine": lambda: mine(game_data, game_content),
            "gather": lambda: gather(game_data, game_content),
            "rest": lambda: rest(game_data),
            "status": lambda: player.status(game_data),
            "shop": lambda: shop(game_data, game_content),
            "crafting": lambda: crafting(game_data, game_content),
            "restart": lambda: player.restart(game_data, game_content),
            "switch character": lambda: player.switch_character(game_data)
        }

        # Validate actions with options being possible actions
        action = validate(
            possible_actions,
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
