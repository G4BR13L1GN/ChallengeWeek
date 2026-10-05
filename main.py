import random
import json


# Utility Functions
def SaveToJson(gameData):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(gameData, f, indent=4, ensure_ascii=False)


def Validate(options, message):
    value = ""

    while value not in options:
        value = str(input(f"{message}").lower())

        if value not in options:
            print("Invalid input\n")

    return value


def DiceRoll(maxRoll = 20):
    # Roll a random int from 1 to maxRoll, 20 if no amount is given
    return random.randint(1, maxRoll)


def ResetData(gameData):
    # Assign player data variables
    playerData = gameData.get("PlayerData")
    playerProgress = playerData.get("PlayerProgress")

    # Reset player data
    for part in (playerProfile := playerData.get("PlayerProfile")).keys():
        playerProfile[part] = ""

    for attribute in (playerAttributes := playerData.get("PlayerAttributes")).keys():
        playerAttributes[attribute] = 0

    for condition in (playerCondition := playerData.get("PlayerCondition")).keys():
        playerCondition[condition] = 0

    playerData.get("PlayerSkills").clear()

    playerData.get("PlayerInventory").clear()
    playerData.get("PlayerEquipment").clear()

    playerProgress = playerData.get("PlayerProgress")
    for part in ("Experience", "MapZone", "DaysPassed"):
        playerProgress[part] = 0

    playerProgress["MapDimension"] = "Overworld"

    # Add "coins" to inventory since it is a currency
    playerInventory = playerData.get("PlayerInventory")
    playerInventory["coins"] = {
        "Amount": 0,
        "Price": 1
    }

    # Save cleared player inventory
    SaveToJson(gameData)


def Restart(gameData):
    # Only continue if player has agreed twice
    if str(input("Do you really want to restart? (Y/N)\n> ").upper()) == "Y" and \
       str(input("\nAre you sure? (Y/N)\n> ").upper()) == "Y":
        # Set up new character
        CharacterSetup(gameData)


# Gameplay Functions
def CharacterSetup(gameData):
    # Reset data so there is no save conflict
    ResetData(gameData)

    # Assign playerData and classData
    playerData = gameData.get("PlayerData")
    playerProfile = playerData.get("PlayerProfile")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")
    playerSkills = playerData.get("PlayerSkills")

    classData = gameData.get("ClassData")

    # Assign name
    playerName = str(input("\nWhat is your characters name?\n> "))
    playerProfile["Name"] = playerName

    # Loop until valid player class is chosen
    playerClass = Validate(
        (classes := classData.keys()), 
        f"\nWhat is your characters class?\n{", ".join(classes)}\n> "
    )

    # Assign class once
    playerProfile["Class"] = playerClass

    # Assign each attribute based on class
    for attribute in ("Strength", "Dexterity", "Intelligence"):
        playerAttributes[attribute] = classData[playerClass][attribute]

    # Assign health and stamina based on class
    for condition in ("Health", "Stamina"):
        playerCondition[condition] = classData[playerClass][condition]

    # Assign max health and stamina with slicing
    for condition in ("MaxHealth", "MaxStamina"):
        playerCondition[condition] = playerCondition[condition[3:]]

    # Add class skills to playerSkills
    playerSkills.extend(classData[playerClass]["Skills"])

    # Welcome player and display stats
    print(f"\nWelcome {playerName} the {playerClass}!\n")

    print(f"Your stats are:\n"
          f"Attributes: {", ".join([f"{key}: {value}" for key, value in playerAttributes.items()])}\n"
          f"Condition: {", ".join([f"{key}: {value}" for key, value in list(playerCondition.items())[::2]])}\n"
          f"Skills: {", ".join([skill.capitalize() for skill in playerSkills])}"
    )

    # Update gameData json file
    SaveToJson(gameData)


def Quit(gameData):
    # Update gameData json file
    SaveToJson(gameData)

    quit()


def Combat(gameData, enemyClass, mapDimension, monsterName):
    # Define enemy statistics based off of arguments
    enemyData = gameData.get("MonsterData")[mapDimension][enemyClass][monsterName]
    enemyHealth = enemyData.get("Health")
    enemyDamage = enemyData.get("Damage")

    # Define player statistics
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")
    playerAttributes = playerData.get("PlayerAttributes")
    playerEquipment = playerData.get("PlayerEquipment")
    playerSkills = playerData.get("PlayerSkills")

    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Set buff counter
    buffTurns = 0

    # Loop combat until either player or enemy dies
    while currentHealth > 0 and enemyHealth > 0:
        # Repeat loop if action is not in playerSkills
        action = Validate(
            ("attack", "defence", "support"),
            f"\nWhat would {playerName} like to do?\nattack, defence, support\n> "
        )

        # Empty line after checking attack
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
        defenceMultiplier *= 1.2 if buffTurns > 0 else 1

        # Remove buff counter
        buffTurns -= 1 if buffTurns > 0 else 0

        # Different functions based on action
        match action:
            case "attack":
                types = ("melee", "ranged", "spell")
                availableTypes = [skill for skill in types if skill in playerSkills]
                
                attackType = Validate(
                    availableTypes, 
                    f"How would {playerName} like to attack?\n{", ".join(availableTypes)}\n> "
                )

                playerDamage = 0

                match attackType:
                    # Deal damage based on attributes, from 0.1 to 2.0x damage
                    case "melee":
                        playerDamage = round(
                            ((playerAttributes.get("Strength") * (DiceRoll(20) / 10)) * attackMultiplier), 
                            0
                        )
                    case "ranged":
                        playerDamage = round(
                            ((playerAttributes.get("Dexterity") * (DiceRoll(20) / 10)) * attackMultiplier),
                            0
                        )
                    case "spell":
                        playerDamage = round(
                            ((playerAttributes.get("Intelligence") * (DiceRoll(20) / 10)) * attackMultiplier),
                            0
                        )

                enemyHealth -= playerDamage

                # Limit enemyHealth to 0, not -4 for example
                if enemyHealth < 0:
                    enemyHealth = 0

                print(f"{playerName} did {playerDamage} damage!\nThe {monsterName} has {enemyHealth} HP left.")

            case "defence":
                types = ("block", "dodge", "ward")
                availableTypes = [skill for skill in types if skill in playerSkills]

                defendType = Validate(
                    availableTypes, 
                    f"How would {playerName} like to defend?\n{", ".join(availableTypes)}\n> "
                )

                diceRoll = DiceRoll(20)

                match defendType:
                    case "block":
                        # Double defenceMultiplier if strength * roll > 10
                        defenceMultiplier *= 2 if (
                            playerAttributes.get("Strength") * (diceRoll / 10)
                        ) > 10 else 1
                    case "dodge":
                        # Double defenceMultiplier if dexterity * roll > 10
                        defenceMultiplier *= 2 if (
                            playerAttributes.get("Dexterity") * (diceRoll / 10)
                        ) > 10 else 1
                    case "ward":
                        # Double defenceMultiplier if intelligence * roll > 10
                        defenceMultiplier *= 2 if (
                            playerAttributes.get("Intelligence") * (diceRoll / 10)
                        ) > 10 else 1

                print(
                    f"{playerName} performed a succesful block, damage negation * 2 for this turn!"
                    if diceRoll > 10 
                    else f"{playerName} failed the defence action, no damage negation bonus this turn!"
                )

            case "support":
                types = ("buff", "heal") # add warcry, focus, concentrate instead of general buff
                availableTypes = [skill for skill in types if skill in playerSkills]

                supportType = Validate(
                    availableTypes, 
                    f"How would {playerName} like to defend?\n{", ".join(availableTypes)}\n> "
                )

                match supportType:
                    case "buff":
                        buffTurns = 3
                        print(f"{playerName} applied buff, weapon damage and damage negation * 1.2!")
                    case "heal":
                        # Heal 10 to 30 HP
                        regeneratedHealth = 10 + DiceRoll(20)

                        # Limit regeneratedHealth so currentHealth will not exceed maxHealth
                        if (currentHealth + regeneratedHealth) > maxHealth:
                            regeneratedHealth = maxHealth - currentHealth

                        # Apply healing
                        currentHealth += regeneratedHealth

                        print(
                            f"{playerName} healed {regeneratedHealth} HP!\n"
                            f"{playerName} has {currentHealth} HP left."
                        )

        # Empty line after player action
        print()

        # Continue fight if enemy still alive
        if enemyHealth > 0:
            # Calculate damage dealt by enemy
            damageDealt  = round(((enemyDamage / defenceMultiplier) * (DiceRoll(20) / 10)), 0)
            currentHealth -= damageDealt

            print(f"The {monsterName} did {damageDealt} damage!\n{playerName} has {currentHealth} HP left.")
        else:
            # Reward player with experience and coins with maximum of monster XP
            experienceGained = enemyData.get("Experience", 0)

            print(f"{playerName} defeated the {monsterName} and gained {experienceGained} XP!\n")
            Aquire(gameData, "coins", 100, experienceGained, 1)

            playerProgress = playerData.get("PlayerProgress")
            playerProgress["Experience"] += experienceGained
            break

    if currentHealth <= 0:
        print(f"{playerName} has died!")

        # Update gameData json file
        SaveToJson(gameData)

        return

    # Save player health after battle
    playerCondition["Health"] = currentHealth

    # Increase player zone
    print(f"{playerName} has advanced to next map zone!")
    playerProgress["MapZone"] += 1

    # Increase daysPassed
    playerProgress["DaysPassed"] += 0.5

    # zones = ["Overworld", "Caverns", "Sift"]
    # playerProgress["MapDimension"] = zones[(playerProgress.get("MapZone") - 1) // 6]

    # Update gameData json file
    SaveToJson(gameData)


def Adventure(gameData):
    # Assign player data
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")
    playerProgress = playerData.get("PlayerProgress")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Stamina cost for adventuring
    staminaCost = 10

    # Prevent stamina going below 0
    if (playerCondition["Stamina"] - staminaCost) < 0:
        print(f"{playerName} doesn't have enough stamina to adventure, {playerName} should rest!")
        return

    # Remove stamina from playerCondition
    playerCondition["Stamina"] -= staminaCost

    print(f"{playerName} has used {staminaCost} stamina points to adventure.")

    # Encounter if player intelligence passes sight check
    if playerAttributes.get("Intelligence") > DiceRoll(20):
        monsterData = gameData.get("MonsterData")

        monsterName = random.choice(list(monsterData[playerProgress.get("MapDimension")]["Monsters"].keys()))
        print(f"{playerName} encountered a {monsterName}")

        Combat(gameData, "Monsters", playerProgress.get("MapDimension"), monsterName)
    else:
        print(f"{playerName} encountered nothing.")

    # Increase daysPassed
    playerProgress["DaysPassed"] += 0.5

    # Update gameData json file
    SaveToJson(gameData)


def Aquire(gameData, itemName, spawnPercentage = 20, maxSpawnAmount = 5, itemPrice = 10):
    # Aquire item with gameData to add item onto, name of item, spawn chance, max spawn amount, and price
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    # random chance from 1 to spawnChance, which accepts that is or is under 1
    if random.uniform(0, 100 / spawnPercentage) <= 1:
        spawnAmount = random.randint(1, maxSpawnAmount)
        print(f"{playerData.get("PlayerProfile").get("Name")} got {spawnAmount} {itemName}!")

        # .get() can give existing amount, or 0 if it doesn't exist yet
        playerInventory[itemName] = {
            "Amount": playerInventory.get(itemName, {}).get("Amount", 0) + spawnAmount,
            "Price": itemPrice
        }

    # Update gameData json file
    SaveToJson(gameData)


def Mine(gameData):
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Stamina cost for mining
    staminaCost = 10

    # Prevent stamina going below 0
    if (playerCondition["Stamina"] - staminaCost) < 0:
        print(f"{playerName} doesn't have enough stamina to mine, {playerName} should rest!")
        return

    playerCondition["Stamina"] -= staminaCost

    print(
        f"{playerName} has used {staminaCost} stamina points to mine, "
        f"and now has {playerCondition.get("Stamina")} stamina left."
    )

    # Higher chance on materials if strength is high
    mineFactor = playerAttributes.get("Strength") / 10

    # Mining materials which can be found
    Aquire(gameData, "coal", 100 / mineFactor, 4, 2)
    Aquire(gameData, "iron", 50 / mineFactor, 4, 4)
    Aquire(gameData, "silver", 33 / mineFactor, 3, 6)
    Aquire(gameData, "gold", 25 / mineFactor, 3, 10)
    Aquire(gameData, "diamond", 5 / mineFactor, 2, 20)

    # Increase daysPassed
    playerData.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update gameData json file
    SaveToJson(gameData)


def Gather(gameData):
    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")
    playerCondition = playerData.get("PlayerCondition")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Stamina cost for gathering
    staminaCost = 10

    # Prevent stamina going below 0
    if (playerCondition["Stamina"] - staminaCost) < 0:
        print(f"{playerName} doesn't have enough stamina to adventure, {playerName} should rest!")
        return

    playerCondition["Stamina"] -= staminaCost

    print(
        f"{playerName} has used {staminaCost} stamina points to gather, "
        f"and now has {playerCondition.get("Stamina")} stamina left."
    )

    # Higher chance on materials if dexterity is high
    gatherFactor = playerAttributes.get("Dexterity") / 10

    # Forest materials which can be found
    Aquire(gameData, "coins", 50 / gatherFactor, 20, 1)
    Aquire(gameData, "wood", 100 / gatherFactor, 4, 2)
    Aquire(gameData, "berries", 100 / gatherFactor, 3, 2)
    Aquire(gameData, "fruit", 50 / gatherFactor, 3, 3)
    Aquire(gameData, "mysterious potion", 20 / gatherFactor, 2, 10)
    Aquire(gameData, "mysterious blade", 1 / gatherFactor, 1, 100)

    # Increase daysPassed
    playerData.get("PlayerProgress")["DaysPassed"] += 0.5

    # Update gameData json file
    SaveToJson(gameData)


def Rest(gameData):
    # Define player statistics
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Define health and stamina
    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")

    currentStamina = playerCondition.get("Stamina")
    maxStamina = playerCondition.get("MaxStamina")

    # Ask player for short or long rest
    action = Validate(
        ("long", "short"), 
        f"How long would {playerName} like to rest?\nlong, short\n> "
    )

    # Calculate regenerated health and stamina based on rest time
    regeneratedHealth = (maxHealth * 1) if action == "long" else (maxHealth * 0.25)
    regeneratedStamina = (maxStamina * 1) if action == "long" else (maxStamina * 0.5)

    # Limit regeneratedHealth so currentHealth will not exceed maxHealth
    if (currentHealth + regeneratedHealth) > maxHealth:
        regeneratedHealth = maxHealth - currentHealth

    # Limit regeneratedStamina so currentStamina will not exceed maxHealth
    if (currentStamina + regeneratedStamina) > maxStamina:
        regeneratedStamina = maxStamina - currentStamina

    # Add regenerated health and stamina onto current
    currentHealth += regeneratedHealth
    currentStamina += regeneratedStamina

    print(
        f"\n{playerName} regenerated {regeneratedHealth} health.\n{playerName} now has {currentHealth} HP."
        f"{playerName} regained {regeneratedStamina} stamina.\n{playerName} now has {currentStamina} stamina."
    )

    # Save player health and stamina
    playerCondition["Health"] = currentHealth
    playerCondition["Stamina"] = currentStamina

    # Increase daysPassed based on rest length
    playerData.get("PlayerProgress")["DaysPassed"] += 1 if action == "long" else 0.5

    # Update gameData json file
    SaveToJson(gameData)


def Buy(gameData):
    # Define player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")
    playerEquipment = playerData.get("PlayerEquipment")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Define shop items
    shopData = gameData.get("ShopData")

    # Get input for which item player wants to buy
    item = Validate(
        shopItems := list(shopData.keys()), 
        f"What item would {playerName} like to browse?\nThe shop currently has:\n{", ".join(shopItems)}\n> "
    )

    # Print price of item
    itemPrice = shopData.get(item).get("Price")

    print(f"\nThe {item} costs {itemPrice} coins.")

    buyConfirmation = Validate(
        ("y", "n"), 
        f"Would {playerName} like to buy the {item}? (Y/N)\n> "
    )

    if buyConfirmation == "Y":
        if playerInventory.get("coins", {}).get("Amount") >= itemPrice:
            Aquire(gameData, item, 100, 1, itemPrice)
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
            print(f"{playerName} doesn't have enough coin.")
    elif buyConfirmation == "N":
        print()
        Shop(gameData)

    # Update gameData json file
    SaveToJson(gameData)


def Sell(gameData):
    # Define player data
    playerData = gameData.get("PlayerData")
    playerInventory = playerData.get("PlayerInventory")

    playerName = playerData.get("PlayerProfile").get("Name")

    # Get input for which item player wants to buy
    item = Validate(
        # [1:] so it will exclude coins, and turn to list since you can't slice dict.keys()
        inventoryItems := list(playerInventory.keys())[1:],
        f"What item would {playerName} like to sell? {playerName} currently has:\n{", ".join(inventoryItems)}\n> "
    )

    # Print price of item
    print(f"\nThe {item} sells for {playerInventory.get(item).get("Price")} coins.")

    # Ask for confirmation to sell item
    sellConfirmation = Validate(
        ("y", "n"), 
        f"Would {playerName} like to sell the {item}? (Y/N)\n> "
    )

    if sellConfirmation == "Y":
        if playerInventory.get(item).get("Amount") > 0:
            # Not aquire for coins since coins already exists in json at character creation
            playerInventory["coins"]["Amount"] += playerInventory.get(item).get("Price")
            playerInventory[item]["Amount"] -= 1

            # Remove item from inventory if 0 left
            if playerInventory[item].get("Amount") <= 0:
                playerInventory.pop(item)
        else:
            print(f"{playerName} doesn't have enough {item}.")
    elif sellConfirmation == "N":
        print()
        Shop(gameData)

    # Update gameData json file
    SaveToJson(gameData)


def Shop(gameData):
    action = Validate(
        ("buy", "sell", "leave"), 
        f"What would {gameData.get("PlayerData").get("PlayerProfile").get("Name")} "
        f"like to do in the shop?\nbuy, sell, leave\n> "
    )

    # Empty line after player action
    print()

    match action:
        case "buy":
            Buy(gameData)
        case "sell":
            Sell(gameData)
        case "leave":
            return

    # Increase daysPassed
    gameData.get("PlayerData").get("PlayerProgress")["DaysPassed"] += 0.5

    # Update gameData json file
    SaveToJson(gameData)


def Status(gameData):
    # Assign player data
    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")
    playerProgress = playerData.get("PlayerProgress")
    playerName = playerData.get("PlayerProfile").get("Name")

    print(f"It is currently day {round(playerProgress.get("DaysPassed"), 0)}.")

    print(
        f"{playerName} currently has {playerCondition.get("Health")} HP "
        f"and {playerCondition.get("Stamina")} stamina."
    )

    print(
        f"{playerName} currently has {playerProgress.get("Experience")} XP points, "
        f"and is located in map zone {playerProgress.get("MapZone")} "
        f"in the \"{playerProgress.get("MapDimension")}.\""
    )


def Main():
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    playerData = gameData.get("PlayerData")
    playerProfile = playerData.get("PlayerProfile")

    if playerProfile.get("Class") == "":
        CharacterSetup(gameData)

    while True:
        # Reassign gameData after each action
        with open("data.json", "r", encoding = "utf-8") as f:
            gameData = json.load(f)

        # Possible actions with gameData as argument
        possibleActions = {
            "quit": Quit,
            "adventure": Adventure,
            "mine": Mine,
            "gather": Gather,
            "rest": Rest,
            "status": Status,
            "shop": Shop,
            "restart": Restart
        }

        action = Validate(
            possibleActions, 
            f"\nWhat would {gameData.get("PlayerData").get("PlayerProfile").get("Name")} "
            f"like to do?\n{", ".join(list(possibleActions))}\n> "
        )

        # Empty line after player action
        print()

        if action in possibleActions:
            possibleActions[action](gameData)
        else:
            print("Invalid action")


if __name__ == "__main__":
    Main()