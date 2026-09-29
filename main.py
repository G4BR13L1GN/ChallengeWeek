import random
import json


def ResetData(gameData):
    # Assign playerInventory and playerExperience
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")
    playerExperience = playerData.get("PlayerExperience")
    playerProfile = playerData.get("PlayerProfile")

    # Reset player data
    playerInventory.clear()
    playerExperience["Experience"] = 0
    playerProfile["Name"] = ""
    playerProfile["Class"] = ""

    # Save cleared player inventory
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)

    # Idea: reset inventory, levels, xp, with dict.clear()


def Restart(gameData):
    # Only continue if player has agreed twice
    if str(input(f"Do you really want to restart? (Y/N)\n> ").upper()) == "Y" and str(input(f"\nAre you sure? (Y/N)\n> ").upper()) == "Y":
        ResetData(gameData)
        CharacterSetup(gameData)


def CharacterSetup(gameData):
    # Reset data so there is no save conflict
    ResetData(gameData)

    # Assign playerProfile and classData
    classData = gameData.get("ClassData")

    playerData = gameData.get("PlayerData")
    playerProfile = playerData.get("PlayerProfile")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")
    # Idea: change playerSkills based on class

    # Assign name
    playerProfile["Name"] = str(input("\nWhat is your characters name?\n> "))
    print()

    # Loop until class is valid
    playerClass = ""

    while playerClass not in list(classData.keys()):
        playerClass = str(input(f"What is your characters class?\n{list(classData.keys())}\n> "))

        if playerClass not in list(classData.keys()):
            print("Class not available (yet)")
            print()
    
    playerProfile["Class"] = playerClass

    # Assign each attribute based on class
    for attribute in ["Strength", "Dexterity", "Intelligence"]:
        playerAttributes[attribute] = classData[playerClass][attribute]

    # Assign health and stamina based on class
    playerCondition["Health"] = classData[playerClass].get("Health")
    playerCondition["MaxHealth"] = playerCondition.get("Health")

    playerCondition["Stamina"] = classData[playerClass].get("Stamina")
    playerCondition["MaxStamina"] = playerCondition.get("Stamina")

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Quit():
    quit()


def DiceRoll(rollAmount = 20):
    # Return random int from 1 to rollAmount, 20 if no amount given
    return random.randint(1, rollAmount)


def Combat(gameData, monsterName, enemyClass):
    # Define enemy statistics
    enemyData = gameData.get("MonsterData")[enemyClass][monsterName]

    monsterHealth = enemyData.get("Health")
    monsterDamage = enemyData.get("Damage")

    # Define player statistics
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")
    playerAttributes = playerData.get("PlayerAttributes")

    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Set buff counter
    buffTurns = 0

    # Loop combat until either player or enemy dies
    while currentHealth > 0 and monsterHealth > 0:
        # Repeat loop if action is not in playerSkills
        action = str(input(f"How would {playerName} like to attack?\n{playerData.get("PlayerSkills")}\n> ")).capitalize()

        if action not in playerData.get("PlayerSkills"):
            print("Invalid action\n")
            continue

        print()

        # Apply / remove buff, >= because buffTurns removes 1 before attack is possible
        attackMultiplier = 1.2 if buffTurns >= 0 else 1

        if buffTurns > 0:
            buffTurns -= 1

        match action:
            case "Attack":
                playerDamage = (playerAttributes.get("Strength") + DiceRoll(2)) * attackMultiplier
                monsterHealth -= playerDamage

                # Limit monsterHealth to 0, not -4
                if monsterHealth < 0:
                    monsterHealth = 0

                print(f"{playerName} did {playerDamage} damage!\nThe {monsterName} has {monsterHealth} HP left.")
            case "Heal":
                healAmount = 20

                # Limit healAmount if currentHealth will exceed maxHealth with healAmount
                if currentHealth + healAmount > playerCondition.get("MaxHealth"):
                    healAmount = maxHealth - currentHealth
                
                currentHealth += healAmount
                
                print(f"{playerName} healed {healAmount} HP!\n{playerName} has {currentHealth} HP left.")
            case "Buff":
                buffTurns = 3
                print(f"{playerName} applied buff, weapon now does 1.2x damage!")

        print()

        if monsterHealth > 0:
            currentHealth -= monsterDamage
            print(f"The {monsterName} did {monsterDamage} damage!\n{playerName} has {currentHealth} HP left.")
        else:
            experienceGained = enemyData.get("Experience", 0)

            # Reward player with experience and coins with maximum of monster XP
            print(f"{playerName} defeated the {monsterName}!\n{playerName} gained {experienceGained} XP!")
            Aquire(gameData, "Coins", 1, experienceGained, 1)

            playerExperience = playerData.get("PlayerExperience")
            playerExperience["Experience"] += experienceGained
            break

        print()

    # Save player health after battle
    playerCondition["Health"] = currentHealth

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Adventure(gameData):
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")

    # Encounter if player intelligence passes sight check
    if playerAttributes.get("Intelligence") > DiceRoll(1): # CHANGE TO 20
        monsterData = gameData.get("MonsterData")

        monsterName = random.choice(list(monsterData["Monsters"].keys()))
        print(f"{playerData.get("PlayerProfile").get("Name")} encountered a {monsterName}")
        Combat(gameData, monsterName, "Monsters")
    else:
        print(f"{playerData.get("PlayerProfile").get("Name")} encountered nothing")


def Aquire(gameData, itemName, spawnChance, maxSpawnAmount, itemPrice):
    # Aquire item with arguments gameData which it adds items ontop of, 
    #                            name of the item, 
    #                            spawn chance (from 1 to x), 
    #                            max spawn amount,
    #                            and price of the item
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    if random.randint(1, spawnChance) == 1:
        spawnAmount = random.randint(1, maxSpawnAmount)
        print(f"{playerData.get("PlayerProfile").get("Name")} got {spawnAmount} {itemName}!")

        # .get() can give existing amount, or 0 if it doesn't exist yet
        playerInventory[itemName] = {
            "Amount": playerInventory.get(itemName, {}).get("Amount", 0) + spawnAmount,
            "Price": itemPrice
        }

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Mine(gameData):
    Aquire(gameData, "Coal", 1, 4, 2)
    Aquire(gameData, "Iron", 2, 4, 4)
    Aquire(gameData, "Silver", 3, 3, 6)
    Aquire(gameData, "Gold", 4, 3, 10)
    Aquire(gameData, "Diamond", 10, 2, 20)


def Gather(gameData):
    Aquire(gameData, "Coins", 2, 20, 1)
    Aquire(gameData, "Wood", 1, 4, 2)
    Aquire(gameData, "Berries", 1, 3, 2)
    Aquire(gameData, "Fruit", 2, 3, 3)
    Aquire(gameData, "Mysterious potion", 5, 2, 10)
    Aquire(gameData, "Mysterious blade", 100, 1, 100)


def Rest(gameData):
    # Define player statistics
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")

    playerName = playerData.get("PlayerProfile").get("Name")

    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")
    regeneratedHealth = int(maxHealth * 0.15) # +15% health

    currentStamina = playerCondition.get("Stamina")
    maxStamina = playerCondition.get("MaxStamina")
    regeneratedStamina = maxStamina - currentStamina

    # Limit regeneratedHealth if currentHealth will exceed maxHealth with regeneratedHealth
    if currentHealth + regeneratedHealth > maxHealth:
        regeneratedHealth = maxHealth - currentHealth

    # Regenerate health
    currentHealth += regeneratedHealth
    if currentHealth > maxHealth:
        currentHealth = maxHealth

    # Regenerate stamina
    currentStamina += regeneratedStamina

    print(f"{playerName} regenerated {regeneratedHealth} health.\n{playerName} now have {currentHealth} HP.")
    print(f"{playerName} regained {regeneratedStamina} stamina.\n{playerName} now have {currentStamina} stamina.")

    # Save player health and stamina
    playerCondition["Health"] = currentHealth
    playerCondition["Stamina"] = currentStamina

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Buy(gameData):
    # Define player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    # Define shop items
    shopData = gameData.get("ShopData")

    # Get input for which item player wants to buy
    item = ""
    while item not in list(shopData.keys()):
        item = str(input(f"What item would {playerData.get("PlayerProfile").get("Name")} like to browse?\nThe shop currently has: {list(shopData.keys())}\n> ").capitalize())

        if item not in list(shopData.keys()):
            print("Invalid item")
            print()

    # Print price of item
    print()
    print(f"The {item} costs {shopData.get(item).get("Price")} coins.")

    buyConfirmation = ""
    while buyConfirmation not in ["Y", "N"]:
        # Ask for confirmation to buy item
        buyConfirmation = str(input(f"Would {playerData.get("PlayerProfile").get("Name")} like to buy the {item}? (Y/N)\n> ")).capitalize()

        if buyConfirmation == "Y":
            if playerInventory.get("Coins", 0) >= shopData.get(item):
                Aquire(gameData, item, 1, 1, shopData.get(item))
                playerInventory["Coins"]["Amount"] -= shopData.get(item)
            else:
                print(f"{playerData.get("PlayerProfile").get("Name")} does not have enough coin.")
        elif buyConfirmation == "N":
            print()
            Shop()
        else:
            print("Invalid action")
            print()
            continue

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Sell(gameData):
    # Define player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    # Get input for which item player wants to buy
    item = ""
    while item not in list(playerInventory.keys()):
        item = str(input(f"What item would {playerData.get("PlayerProfile").get("Name")} like to sell?\n{playerData.get("PlayerProfile").get("Name")} currently has: {list(playerInventory.keys())}\n> ").capitalize())

        if item not in list(playerInventory.keys()):
            print("Invalid item")
            print()

    # Print price of item
    print()
    print(f"The {item} sells for {playerInventory.get(item).get("Price")} coins.")

    sellConfirmation = ""
    while sellConfirmation not in ["Y", "N"]:
        # Ask for confirmation to sell item
        sellConfirmation = str(input(f"Would {playerData.get("PlayerProfile").get("Name")} like to sell the {item}? (Y/N)\n> ")).capitalize()

        if sellConfirmation == "Y":
            if playerInventory.get(item).get("Amount") > 0:
                playerInventory["Coins"]["Amount"] += playerInventory.get(item).get("Price")
                playerInventory[item]["Amount"] -= 1

                # Remove item from inventory if 0 left
                if playerInventory[item].get("Amount") <= 0:
                    playerInventory.pop(item)
            else:
                print(f"{playerData.get("PlayerProfile").get("Name")} does not have enough {item}.")
        elif sellConfirmation == "N":
            print()
            Shop()
        else:
            print("Invalid action")
            print()
            continue

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Shop(gameData):
    action = str(input(f"What would {gameData.get("PlayerData").get("PlayerProfile").get("Name")} like to do in the shop? (Buy / Sell)\n> ")).capitalize()
    print()

    match action:
        case "Buy":
            Buy(gameData)
        case "Sell":
            Sell(gameData)
        case _:
            print("Invalid action")


def Main():
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    playerData = gameData.get("PlayerData")
    playerProfile = playerData.get("PlayerProfile")

    if playerProfile.get("Name") == "" or playerProfile.get("Class") == "":
        CharacterSetup(gameData)

    # Reassign playerProfile with new name
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    while True:
        action = str(input(f"\nWhat would {gameData.get("PlayerData").get("PlayerProfile").get("Name")} like to do?\n> ")).capitalize()
        print()

        # Possible actions, with lambda to insert gameData
        possibleAction = {
            "Quit": Quit,
            "Adventure": lambda: Adventure(gameData),
            "Mine": lambda: Mine(gameData),
            "Gather": lambda: Gather(gameData),
            "Rest": lambda: Rest(gameData),
            "Shop": lambda: Shop(gameData),
            "Restart": lambda: Restart(gameData)
        }

        if action in possibleAction:
            possibleAction[action]()
        else:
            print("Invalid action")


if __name__ == "__main__":
    Main()