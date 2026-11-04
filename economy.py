import random
from utils import validate, save_to_json, get_player_data


# = ECONOMY FUNCTIONS
# Function to add item to player based on spawn chances
def add_item(game_data, item_name, amount, price, message=True):
    # Add item to game inventory
    player_data = get_player_data(game_data)
    player_inventory = player_data.get("PlayerInventory")

    if message:
        print(
            f"\n{player_data.get("PlayerProfile").get("Name")} "
            f"got {amount} {item_name}{"s" if amount > 1 else ""}!"
        )

    player_inventory[item_name] = {
        "Amount": player_inventory.get(item_name, {}).get("Amount", 0) + amount,
        "Price": price
    }

    # Update game_data json file
    save_to_json(game_data)


# Aquire item with game_data to add item onto, name of item, spawn chance, max spawn amount, and price
def aquire(game_data, item_name, spawn_percentage=20, max_spawn_amount=5, spawn_all=False, item_price=10):
    # Random chance from 1 to spawn_percentage, which accepts that is or is under 1
    if random.uniform(0, 100 / spawn_percentage) <= 1:
        if spawn_all:
            spawn_amount = max_spawn_amount
        else:
            spawn_amount = random.randint(1, max_spawn_amount)

        # Add item to inventory
        add_item(game_data, item_name, spawn_amount, item_price)

    # Update game_data json file
    save_to_json(game_data)


# Buy item from shop
def buy(game_data, game_content):
    # Define player data
    player_data = get_player_data(game_data)
    player_inventory = player_data.get("PlayerInventory")
    player_equipment = player_data.get("PlayerEquipment")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Define shop items
    shop_data = game_content.get("ShopData")
    item_data = game_content.get("ItemData")

    # Get input for which item player wants to buy
    item = validate(
        shop_items := shop_data,
        f"What item would {player_name} like to browse?\n"
        f"The shop currently has:\n{", ".join(shop_items)}\n> "
    )

    # Print price of item
    item_price = item_data.get(item).get("Price")

    print(f"\nEach {item} costs {item_price} coins.")

    # Ask how many player wants to buy, max amount is either 99 or how much player can buy
    buy_amount = validate(
        range(1, min(100, (player_inventory.get("coins").get("Amount") // item_price))),
        f"\nHow much of {item} would you like to buy?\n1 - 99\n> ",
        int
    )

    # Confirmation to buy
    buy_confirmation = validate(
        ("y", "n"),
        f"\nWould {player_name} like to buy the {item}{"s" if buy_amount > 1 else ""}? (Y/N)\n> "
    )

    # Check if confirmation is yes
    if buy_confirmation == "y":
        # Check if player has enough coin
        if player_inventory.get("coins", {}).get("Amount") >= item_price * buy_amount:
            # Add item to inventory, remove coins
            add_item(game_data, item, buy_amount, item_price, False)
            player_inventory["coins"]["Amount"] -= item_price * buy_amount

            # Print what player bought
            print(f"{player_name} bought {buy_amount} "
                  f"{item}{"s" if buy_amount > 1 else ""} "
                  f"for {buy_amount * item_price} coins!")

            # Add item to player_equipment for specific types
            if item_data.get(item).get("Type") in ["Weapon", "Armour"]:
                # Get item type
                player_equipment[item] = {
                    "Type": item_data.get(item).get("Type")
                }

                # Add item to player equipment based on if it is weapon or armor
                if item_data.get(item).get("Type") == "Weapon":
                    player_equipment[item]["DamageIncrease"] = item_data.get(
                        item).get("DamageIncrease")

                elif item_data.get(item).get("Type") == "Armour":
                    player_equipment[item]["DamageNegation"] = item_data.get(
                        item).get("DamageNegation")
        else:
            print(f"{player_name} doesn't have enough coin.")

    # Return if player does not want to buy
    elif buy_confirmation == "n":
        return

    # Update game_data json file
    save_to_json(game_data)


# Sell item to shop
def sell(game_data):
    # Define player data
    player_data = get_player_data(game_data)
    player_inventory = player_data.get("PlayerInventory")

    player_name = player_data.get("PlayerProfile").get("Name")

    # Get input for which item player wants to buy, if player has items to sell
    if len(player_inventory.keys()) > 1:
        item = validate(
            # [1:] so it will exclude coins, and turn to list since you can't slice dict.keys()
            inventory_items := list(player_inventory.keys())[1:],
            f"\nWhat item would {player_name} like to sell? "
            f"{player_name} currently has:\n{", ".join(inventory_items)}\n> "
        )
    else:
        print(f"{player_name} has nothing to sell!")
        return

    # Print price of item, reduced sell price
    item_price = player_inventory.get(item).get("Price") * 0.8

    print(
        f"Each {item} sells for "
        f"{item_price} coins."
    )

    # Ask how many player wants to sell
    max_sell_amount = player_inventory.get(item).get("Amount")

    sell_amount = validate(
        range(1, max_sell_amount + 1),
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
            add_item(game_data, "coins", item_price * sell_amount, item_price, False)
            player_inventory[item]["Amount"] -= sell_amount

            print(
                f"\n{player_name} sold {sell_amount} "
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
    player_data = get_player_data(game_data)

    action = validate(
        ("buy", "sell", "leave"),
        f"What would {player_data.get("PlayerProfile").get("Name")} "
        f"like to do in the shop?\nbuy, sell, leave\n> "
    )

    # Empty line after player action
    print()

    match action:
        case "buy":
            buy(game_data, game_content)
        case "sell":
            sell(game_data)
        case "leave":
            return

    # Increase days_passed
    player_data.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update game_data json file
    save_to_json(game_data)


def crafting(game_data, game_content):
    # Assign player data and item data
    player_data = get_player_data(game_data)
    player_name = player_data.get("PlayerProfile").get("Name")
    player_inventory = player_data.get("PlayerInventory")

    item_data = game_content.get("ItemData")

    # Get all craftable items by filtering through items that have a recipe
    craftable_items = tuple(key for key, value in item_data.items() if value.get("Recipe", {}) != {})

    # Validate item to craft
    item_to_craft = item_data.get(validate(
        craftable_items,
        f"What item would {player_name} like to craft?\n{", ".join(craftable_items)}\n> ",
        str
    ))

    item_name = list(item_to_craft.values())[0].lower()

    # Get recipe for item
    recipe = item_to_craft.get("Recipe")

    # Print required materials
    print(
        f"\nTo craft the {item_name} you will need:\n"
        f"{"\n".join([f"{value}x {key}" for key, value in recipe.items()])}"
    )

    # List to add how many times able to craft with each material
    materials_list = []

    # Check if player has required materials
    for key, value in recipe.items():
        # Check if player has item
        if key in player_inventory.keys():
            # Check if player has enough of said item
            material_amount = player_inventory.get(key).get("Amount")
            if material_amount < value:
                print(f"{player_name} does not have enough {key}!")
                return

            # Add to materials list floor of how many can craft
            materials_list.append(material_amount // value)
        # Return if required material not in inventory
        else:
            print(f"{player_name} does not have any {key}!")
            return

    # Ask how many player wants to craft, max is lowest of materials_list
    max_craft_amount = min(materials_list)

    craft_amount = validate(
        range(1, max_craft_amount + 1),
        f"\nHow much of {item_name} would you like to craft?\n"
        f"1 - {max_craft_amount}\n> ",
        int
    )

    # Confirmation to craft
    craft_confirmation = validate(
        ("y", "n"),
        f"\nWould {player_name} like to craft the {item_name}{"s" if craft_amount > 1 else ""}? (Y/N)\n> "
    )

    # Check if craft confirmation is yes
    if craft_confirmation == "y":
        # Remove crafting materials from inventory
        for key, value in recipe.items():
            player_inventory[key]["Amount"] -= value * craft_amount

            # Remove item from inventory if 0 left
            if player_inventory[key].get("Amount") <= 0:
                player_inventory.pop(key)

        # Add crafted item to inventory
        add_item(game_data, item_name, craft_amount, item_data.get(item_name).get("Price"), False)
        print(f"\n{item_name} crafted!")

    elif craft_confirmation == "n":
        return

    # Update game_data json file
    save_to_json(game_data)
