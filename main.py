import random
import json


def ResetData(gameData):
    # Assign player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")
    playerEquipment = playerData.get("PlayerEquipment")
    playerProgress = playerData.get("PlayerProgress")
    playerProfile = playerData.get("PlayerProfile")

    # Reset player data
    playerInventory.clear()
    playerEquipment.clear()
    playerProgress["Experience"] = 0
    playerProgress["MapZone"] = 1
    playerProgress["MapDimension"] = "Overworld"

    for part in playerProfile.keys():
        playerProfile[part] = ""

    # Add "Coins" to inventory
    playerInventory = {
        "coins": {
            "Amount": 0,
            "Price": 1
        }
    }

    # Save cleared player inventory
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Restart(gameData):
    # Only continue if player has agreed twice
    if str(input("Do you really want to restart? (Y/N)\n> ").upper()) == "Y" and str(input("\nAre you sure? (Y/N)\n> ").upper()) == "Y":
        # Set up new character
        CharacterSetup(gameData)


def CharacterSetup(gameData):
    # Reset data so there is no save conflict
    ResetData(gameData)

    # Assign playerData and classData
    playerData = gameData.get("PlayerData")
    playerProfile = playerData.get("PlayerProfile")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")

    classData = gameData.get("ClassData")

    # have to change playerSkills based on class

    # Assign name
    playerProfile["Name"] = str(input("\nWhat is your characters name?\n> "))
    print()

    # Loop until class is valid
    playerClass = ""

    # Loop until valid player class is chosen
    while playerClass not in list(classData.keys()):
        playerClass = str(input(f"What is your characters class?\n{", ".join(list(classData.keys()))}\n> ").lower())

        if playerClass not in list(classData.keys()):
            print("Class not available (yet)")
            print()

    # Assign class once
    playerProfile["Class"] = playerClass

    # Assign each attribute based on class
    for attribute in ["Strength", "Dexterity", "Intelligence"]:
        playerAttributes[attribute] = classData[playerClass][attribute]

    # Assign health and stamina based on class
    playerCondition["Health"] = classData[playerClass].get("Health")
    playerCondition["MaxHealth"] = playerCondition.get("Health")

    playerCondition["Stamina"] = classData[playerClass].get("Stamina")
    playerCondition["MaxStamina"] = playerCondition.get("Stamina")

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Quit(gameData):
    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)

    quit()


def DiceRoll(rollAmount = 20):
    # Return random int from 1 to rollAmount, 20 if no amount given
    return random.randint(1, rollAmount)


def Combat(gameData, enemyClass, mapDimension, monsterName):
    # Define enemy statistics
    enemyData = gameData.get("MonsterData")[mapDimension][enemyClass][monsterName]
    enemyHealth = enemyData.get("Health")
    enemyDamage = enemyData.get("Damage")

    # Define player statistics
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")
    playerAttributes = playerData.get("PlayerAttributes")
    playerEquipment = playerData.get("PlayerEquipment")

    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Set buff counter
    buffTurns = 0

    print()

    # Loop combat until either player or enemy dies
    while currentHealth > 0 and enemyHealth > 0:
        # Repeat loop if action is not in playerSkills
        action = str(input(f"How would {playerName} like to attack?\n{playerData.get("PlayerSkills")}\n> ")).lower()

        if action not in playerData.get("PlayerSkills"):
            print("Invalid action\n")
            continue

        print()

        # Assign attack and defence multiplier
        attackMultiplier, defenceMultiplier = 1, 1

        # Change attack and defence multiplier based on highest armour rating
        for key in playerEquipment.keys():
            equipment = playerEquipment.get(key)

            if equipment.get("Type") == "Weapon":
                if equipment.get("DamageIncrease") > attackMultiplier:
                    attackMultiplier = equipment.get("DamageIncrease")
            elif equipment.get("Type") == "Armour":
                if equipment.get("DamageNegation") > defenceMultiplier:
                    defenceMultiplier = equipment.get("DamageNegation")

        # Apply / remove buff
        attackMultiplier *= 1.2 if buffTurns > 0 else 1
        defenceMultiplier *= 1

        if buffTurns > 0:
            buffTurns -= 1

        # Different functions based on action
        match action:
            case "attack":
                # Deal strength + 1 or 2 extra damage, multiplied by attackMultiplier to enemy
                playerDamage = int((playerAttributes.get("Strength") + DiceRoll(2)) * attackMultiplier)
                enemyHealth -= playerDamage

                # Limit enemyHealth to 0, not -4 for example
                if enemyHealth < 0:
                    enemyHealth = 0

                print(f"{playerName} did {playerDamage:00} damage!\nThe {monsterName} has {enemyHealth:00} HP left.")
            case "heal":
                # Heal 20 HP
                healAmount = 20

                # Limit healAmount if currentHealth will exceed maxHealth with healAmount
                if currentHealth + healAmount > playerCondition.get("MaxHealth"):
                    healAmount = maxHealth - currentHealth

                # Apply healing
                currentHealth += healAmount

                print(f"{playerName} healed {healAmount} HP!\n{playerName} has {currentHealth} HP left.")
            case "buff":
                # 4 not 3 since buffTurns removes 1 before attack is possible
                buffTurns = 4
                print(f"{playerName} applied buff, weapon now does 1.2x damage!")

        print()

        # Continue fight if enemy still alive
        if enemyHealth > 0:
            currentHealth -= int(enemyDamage / defenceMultiplier)
            print(f"The {monsterName} did {int(enemyDamage / defenceMultiplier)} damage!\n{playerName} has {currentHealth} HP left.")
        else:
            # Reward player with experience and coins with maximum of monster XP
            experienceGained = enemyData.get("Experience", 0)

            print(f"{playerName} defeated the {monsterName}!\n{playerName} gained {experienceGained} XP!")
            Aquire(gameData, "coins", 1, experienceGained, 1)

            playerProgress = playerData.get("PlayerProgress")
            playerProgress["Experience"] += experienceGained
            break

        print()

    if currentHealth <= 0:
        print(f"{playerName} has died!")

        # Update gameData json file
        with open("data.json", "w", encoding = "utf-8") as f:
            json.dump(gameData, f, indent = 4, ensure_ascii = False)

        return

    # Save player health after battle
    playerCondition["Health"] = currentHealth

    # Increase player zone
    playerProgress["MapZone"] += 1

    # zones = ["Overworld", "Caverns", "Sift"]
    # playerProgress["MapDimension"] = zones[(playerProgress.get("MapZone") - 1) // 6]

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Adventure(gameData):
    # Assign player data
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")
    playerProgress = playerData.get("PlayerProgress")

    # Stamina cost for adventuring
    staminaCost = 10

    # Prevent stamina going below 0
    if (playerCondition["Stamina"] - staminaCost) < 0:
        print(f"{playerData.get("PlayerProfile").get("Name")} doesn't have enough stamina to adventure, {playerData.get("PlayerProfile").get("Name")} should rest!")
        return

    playerCondition["Stamina"] -= staminaCost

    print(f"{playerData.get("PlayerProfile").get("Name")} has used {staminaCost} stamina points to adventure.")

    # Encounter if player intelligence passes sight check
    if playerAttributes.get("Intelligence") > DiceRoll(20):
        monsterData = gameData.get("MonsterData")

        monsterName = random.choice(list(monsterData[playerProgress.get("MapDimension")]["Monsters"].keys()))
        print(f"{playerData.get("PlayerProfile").get("Name")} encountered a {monsterName}")

        Combat(gameData, "Monsters", playerProgress.get("MapDimension"), monsterName)
    else:
        print(f"{playerData.get("PlayerProfile").get("Name")} encountered nothing.")


def Aquire(gameData, itemName, spawnChance = 5, maxSpawnAmount = 5, itemPrice = 10):
    # Aquire item with arguments gameData which it adds items ontop of,
    #                            name of the item,
    #                            spawn chance (from 1 to x),
    #                            max spawn amount,
    #                            and price of the item
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    # random chance from 1 to spawnChance, which accepts that is or is under 1
    if random.uniform(0, spawnChance) <= 1:
        spawnAmount = random.randint(1, maxSpawnAmount)
        print(f"{playerData.get("PlayerProfile").get("Name")} got {spawnAmount} {itemName}!")

        # .get() can give existing amount, or 0 if it doesn't exist yet
        playerInventory[itemName] = {
            "Amount": playerInventory.get(itemName, {}).get("Amount", 0) + spawnAmount,
            "Price": itemPrice
        }

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Mine(gameData):
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")

    # Stamina cost for mining
    staminaCost = 10

    # Prevent stamina going below 0
    if (playerCondition["Stamina"] - staminaCost) < 0:
        print(f"{playerData.get("PlayerProfile").get("Name")} doesn't have enough stamina to mine, {playerData.get("PlayerProfile").get("Name")} should rest!")
        return

    playerCondition["Stamina"] -= staminaCost

    print(f"{playerData.get("PlayerProfile").get("Name")} has used {staminaCost} stamina points to mine, and now has {playerCondition.get("Stamina")} stamina left.")

    # Higher chance on materials if strength is high
    mineFactor = playerAttributes.get("Strength") / 10

    # Mining materials which can be found
    Aquire(gameData, "coal", 1 / mineFactor, 4, 2)
    Aquire(gameData, "iron", 2 / mineFactor, 4, 4)
    Aquire(gameData, "silver", 3 / mineFactor, 3, 6)
    Aquire(gameData, "gold", 4 / mineFactor, 3, 10)
    Aquire(gameData, "diamond", 20 / mineFactor, 2, 20)

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Gather(gameData):
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")

    # Stamina cost for gathering
    staminaCost = 10

    # Prevent stamina going below 0
    if (playerCondition["Stamina"] - staminaCost) < 0:
        print(f"{playerData.get("PlayerProfile").get("Name")} doesn't have enough stamina to adventure, {playerData.get("PlayerProfile").get("Name")} should rest!")
        return

    playerCondition["Stamina"] -= staminaCost

    print(f"{playerData.get("PlayerProfile").get("Name")} has used {staminaCost} stamina points to gather, and now has {playerCondition.get("Stamina")} stamina left.")

    # Higher chance on materials if dexterity is high
    gatherFactor = playerAttributes.get("Dexterity") / 10

    # Forest materials which can be found
    Aquire(gameData, "coins", 2 / gatherFactor, 20, 1)
    Aquire(gameData, "wood", 1 / gatherFactor, 4, 2)
    Aquire(gameData, "berries", 1 / gatherFactor, 3, 2)
    Aquire(gameData, "fruit", 2 / gatherFactor, 3, 3)
    Aquire(gameData, "mysterious potion", 5 / gatherFactor, 2, 10)
    Aquire(gameData, "mysterious blade", 100 / gatherFactor, 1, 100)

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Rest(gameData):
    # Define player statistics
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Define health and stamina
    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")
    regeneratedHealth = int(maxHealth * 0.15) # +15% health

    currentStamina = playerCondition.get("Stamina")
    maxStamina = playerCondition.get("MaxStamina")
    regeneratedStamina = maxStamina - currentStamina # fully restore stamina

    # Limit regeneratedHealth if currentHealth will exceed maxHealth with regeneratedHealth
    if currentHealth + regeneratedHealth > maxHealth:
        regeneratedHealth = maxHealth - currentHealth

    # Regenerate health
    currentHealth += regeneratedHealth
    if currentHealth > maxHealth:
        currentHealth = maxHealth

    # Regenerate stamina
    currentStamina += regeneratedStamina

    print(f"{playerName} regenerated {regeneratedHealth} health.\n{playerName} now has {currentHealth} HP.")
    print(f"{playerName} regained {regeneratedStamina} stamina.\n{playerName} now has {currentStamina} stamina.")

    # Save player health and stamina
    playerCondition["Health"] = currentHealth
    playerCondition["Stamina"] = currentStamina

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Buy(gameData):
    # Define player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")
    playerEquipment = playerData.get("PlayerEquipment")

    # Define shop items
    shopData = gameData.get("ShopData")

    # Get input for which item player wants to buy
    item = ""
    while item not in list(shopData.keys()):
        item = str(input(f"What item would {playerData.get("PlayerProfile").get("Name")} like to browse?\nThe shop currently has: {list(shopData.keys())}\n> ").lower())

        if item not in list(shopData.keys()):
            print("Invalid item")
            print()

    # Print price of item
    itemPrice = shopData.get(item).get("Price")

    print()
    print(f"The {item} costs {itemPrice} coins.")

    buyConfirmation = ""
    while buyConfirmation not in ["Y", "N"]:
        # Ask for confirmation to buy item
        buyConfirmation = str(input(f"Would {playerData.get("PlayerProfile").get("Name")} like to buy the {item}? (Y/N)\n> ")).capitalize()

        if buyConfirmation == "Y":
            if playerInventory.get("coins", {}).get("Amount") >= itemPrice:
                Aquire(gameData, item, 1, 1, itemPrice)
                playerInventory["coins"]["Amount"] -= itemPrice

                # Add item to PlayerEquipment for specific types
                if shopData.get(item).get("Type") in ["Weapon", "Armour"]:
                    playerEquipment[item] = {
                        "Type": shopData.get(item).get("Type")
                    }

                    if shopData.get(item).get("Type") == "Weapon":
                        playerEquipment[item]["DamageIncrease"] = shopData.get(item).get("DamageIncrease")
                    elif shopData.get(item).get("Type") == "Armour":
                        playerEquipment[item]["DamageNegation"] = shopData.get(item).get("DamageNegation")

            else:
                print(f"{playerData.get("PlayerProfile").get("Name")} doesn't have enough coin.")
        elif buyConfirmation == "N":
            print()
            Shop(gameData)
        else:
            print("Invalid action")
            print()
            continue

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Sell(gameData):
    # Define player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    # Get input for which item player wants to buy
    item = ""
    while item not in list(playerInventory.keys()):
        item = str(input(f"What item would {playerData.get("PlayerProfile").get("Name")} like to sell?\n{playerData.get("PlayerProfile").get("Name")} currently has: {list(playerInventory.keys())}\n> ").lower())

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
                playerInventory["coins"]["Amount"] += playerInventory.get(item).get("Price")
                playerInventory[item]["Amount"] -= 1

                # Remove item from inventory if 0 left
                if playerInventory[item].get("Amount") <= 0:
                    playerInventory.pop(item)
            else:
                print(f"{playerData.get("PlayerProfile").get("Name")} doesn't have enough {item}.")
        elif sellConfirmation == "N":
            print()
            Shop(gameData)
        else:
            print("Invalid action")
            print()
            continue

    # Update gameData json file
    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Shop(gameData):
    action = str(input(f"What would {gameData.get("PlayerData").get("PlayerProfile").get("Name")} like to do in the shop? (Buy / Sell / Leave)\n> ")).lower()
    print()

    match action:
        case "buy":
            Buy(gameData)
        case "sell":
            Sell(gameData)
        case "leave":
            return
        case _:
            print("Invalid action")
            Shop(gameData)


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
        # Possible actions with gameData as argument
        possibleActions = {
            "quit": Quit,
            "adventure": Adventure,
            "mine": Mine,
            "gather": Gather,
            "rest": Rest,
            "shop": Shop,
            "restart": Restart
        }

        action = str(input(f"\nWhat would {gameData.get("PlayerData").get("PlayerProfile").get("Name")} like to do?\n{list(possibleActions)}\n> ")).lower()
        print()

        if action in possibleActions:
            possibleActions[action](gameData)
        else:
            print("Invalid action")


if __name__ == "__main__":
    Main()