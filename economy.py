import random
from utils import validate, save_to_json


# Function to add item to player based on spawn chances
def aquire(game_data, game_content, item_name, spawn_percentage=20, max_spawn_amount=5, spawn_all=False, item_price=10):
    # Aquire item with game_data to add item onto, name of item, spawn chance, max spawn amount, and price
    player_data = game_data.get("PlayerData")
    player_inventory = player_data.get("PlayerInventory")

    # Random chance from 1 to spawn_percentage, which accepts that is or is under 1
    if random.uniform(0, 100 / spawn_percentage) <= 1:
        if spawn_all:
            spawn_amount = max_spawn_amount
        else:
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


# Buy item from shop
def buy(game_data, game_content):
    # Define player data
    player_data = game_data.get("PlayerData")
    player_inventory = player_data.get("PlayerInventory")
    player_equipment = player_data.get("PlayerEquipment")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Define shop items
    shop_data = game_content.get("ShopData")

    # Get input for which item player wants to buy
    item = validate(
        shop_items := list(shop_data.keys()),
        f"What item would {player_name} like to browse?\n"
        f"The shop currently has:\n{", ".join(shop_items)}\n> "
    )

    # Print price of item
    item_price = shop_data.get(item).get("Price")

    print(f"\nEach {item} costs {item_price} coins.")

    # Ask how many player wants to buy
    buy_amount = validate(
        range(1, 100),
        f"How much of {item} would you like to buy?\n1 - 99\n> ",
        int
    )

    # Confirmation to buy
    buy_confirmation = validate(
        ("y", "n"),
        f"Would {player_name} like to buy the {item}{"s" if buy_amount > 1 else ""}? (Y/N)\n> "
    )

    # Check if confirmation is yes
    if buy_confirmation == "y":
        # Check if player has enough coin
        if player_inventory.get("coins", {}).get("Amount") >= item_price * buy_amount:
            # Add item to inventory, remove coins
            aquire(game_data, game_content, item, 100, buy_amount, True, item_price)
            player_inventory["coins"]["Amount"] -= item_price * buy_amount

            # Print what player bought
            print(f"{player_name} bought {buy_amount} "
                  f"{item}{"s" if buy_amount > 1 else ""} "
                  f"for {buy_amount * item_price} coins!")

            # Add item to player_equipment for specific types
            if shop_data.get(item).get("Type") in ["Weapon", "Armour"]:
                # Get item type
                player_equipment[item] = {
                    "Type": shop_data.get(item).get("Type")
                }

                # Add item to player equipment based on if it is weapon or armor
                if shop_data.get(item).get("Type") == "Weapon":
                    player_equipment[item]["DamageIncrease"] = shop_data.get(
                        item).get("DamageIncrease")

                elif shop_data.get(item).get("Type") == "Armour":
                    player_equipment[item]["DamageNegation"] = shop_data.get(
                        item).get("DamageNegation")
        else:
            print(f"{player_name} doesn't have enough coin.")

    # Return if player does not want to buy
    elif buy_confirmation == "n":
        return

    # Update game_data json file
    save_to_json(game_data)


# Sell item to shop
def sell(game_data, game_content):
    # Define player data
    player_data = game_data.get("PlayerData")
    player_inventory = player_data.get("PlayerInventory")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Get input for which item player wants to buy, if player has items to sell
    if len(player_inventory.keys()) > 1:
        item = validate(
            # [1:] so it will exclude coins, and turn to list since you can't slice dict.keys()
            inventory_items := list(player_inventory.keys())[1:],
            f"What item would {player_name} like to sell? "
            f"{player_name} currently has:\n{", ".join(inventory_items)}\n> "
        )
    else:
        print(f"{player_name} has nothing to sell!")
        return

    # Print price of item, reduced sell price
    item_price = player_inventory.get(item).get("Price") * 0.8

    print(
        f"\nEach {item} sells for "
        f"{item_price} coins."
    )

    # Ask how many player wants to sell
    max_sell_amount = player_inventory.get(item).get("Amount") + 1

    sell_amount = validate(
        range(1, max_sell_amount),
        f"\nHow much of {item} would you like to sell?\n"
        f"1 - {max_sell_amount}\n> ",
        int
    )

    # Ask for confirmation to sell item
    sell_confirmation = validate(
        ("y", "n"),
        f"\nWould {player_name} like to sell the {item}{"s" if sell_amount > 1 else ""}? (Y/N)\n> "
    )

    # Check if sell confirmation is yes
    if sell_confirmation == "y":
        if player_inventory.get(item).get("Amount") > 0:
            # Not aquire for coins since coins already exists in json at character creation
            player_inventory["coins"]["Amount"] += item_price * sell_amount
            player_inventory[item]["Amount"] -= sell_amount

            print(f"{player_name} sold {sell_amount} "
                  f"{item}{"s" if sell_amount > 1 else ""} "
                  f"for {item_price * sell_amount} coins!"
                  )

            # Remove item from inventory if 0 left
            if player_inventory[item].get("Amount") <= 0:
                player_inventory.pop(item)
        else:
            print(f"{player_name} doesn't have enough {item}.")

    elif sell_confirmation == "n":
        return

    # Update game_data json file
    save_to_json(game_data)


# Shop to buy or sell item
def shop(game_data, game_content):
    action = validate(
        ("buy", "sell", "leave"),
        f"What would {game_data.get("PlayerData").get("PlayerProfile").get("Name")} "
        f"like to do in the shop?\nbuy, sell, leave\n> "
    )

    # Empty line after player action
    print()

    match action:
        case "buy":
            buy(game_data, game_content)
        case "sell":
            sell(game_data, game_content)
        case "leave":
            return

    # Increase days_passed
    game_data.get("PlayerData").get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)
