import json
from combat import combat
from player import restart, character_setup, quit_game, status
from economy import shop
from world import adventure, mine, gather, rest
from utils import validate


# Main Function
def main():
    with open("data.json", "r", encoding="utf-8") as f:
        game_data = json.load(f)

    player_data = game_data.get("PlayerData")
    player_profile = player_data.get("PlayerProfile")

    if player_profile.get("Class") == "":
        character_setup(game_data)

    while True:
        # Reassign game_data after each action
        with open("data.json", "r", encoding="utf-8") as f:
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
