import random
import json


def DiceRoll(rollAmount = 20):
    return random.randint(1, rollAmount)


def Restart():
    if str(input(f"Do you really want to restart? (Y/N)\n> ").upper()) == "Y" and str(input(f"Are you sure? (Y/N)\n> ").upper()) == "Y":
        with open("data.json", "r", encoding = "utf-8") as f:
            gameData = json.load(f)

        playerInventory = gameData.get("PlayerInventory")

        playerInventory.clear()

        with open("data.json", "w", encoding = "utf-8") as f:
            json.dump(gameData, f, indent = 4, ensure_ascii = False)

        # Reset inventory, levels, xp, with dict.clear()


def Combat(monsterName, enemyClass):
    # Define enemy statistics
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    enemyData = gameData.get("MonsterData")[enemyClass][monsterName]

    monsterHealth = enemyData.get("Health")
    monsterDamage = enemyData.get("Damage")

    # Define player statistics
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")
    playerAttributes = playerData.get("PlayerAttributes")

    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")

    # Loop combat until either player or enemy dies
    while currentHealth > 0 or monsterHealth > 0:
        action = str(input(f"How would you like to attack?\n{playerData.get("PlayerSkills")}\n> ")).lower()
        print()

        match action:
            case "attack":
                playerDamage = playerAttributes.get("Strength") + DiceRoll(2)
                monsterHealth -= playerDamage

                # Limit monsterHealth to 0, not -4
                if monsterHealth < 0:
                    monsterHealth = 0

                print(f"You did {playerDamage} damage!\nThe {monsterName} has {monsterHealth} HP left.")
            case "heal":
                healAmount = 20

                # Limit healAmount if currentHealth will exceed maxHealth with healAmount
                if currentHealth + healAmount > playerCondition.get("MaxHealth"):
                    healAmount = maxHealth - currentHealth
                
                currentHealth += healAmount
                
                print(f"You healed {healAmount} HP!\nYou have {currentHealth} HP left.")
            case "buff":
                pass
            case _:
                print("Invalid action")

        print()

        if monsterHealth > 0:
            currentHealth -= monsterDamage
            print(f"The {monsterName} did {monsterDamage} damage!\nYou have {currentHealth} HP left.")
        else:
            print(f"You defeated the {monsterName}!\nYou gained {enemyData.get("Experience")} XP!")
            break

    # Save player health after battle
    playerCondition["Health"] = currentHealth

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Adventure():
    # Define player data and monster data if necessary
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    playerData = gameData.get("PlayerData")
    playerAttributes = playerData.get("PlayerAttributes")

    # Encounter if player intelligence passes sight check
    if playerAttributes.get("Intelligence") > DiceRoll(1):
        monsterData = gameData.get("MonsterData")

        monsterName = random.choice(list(monsterData["Monsters"].keys()))
        print(f"You encountered a {monsterName}")
        Combat(monsterName, "Monsters")
    else:
        print("You encountered nothing")


def Aquire(itemName, spawnChance, maxSpawnAmount):
    # Aquire item with arguments name, spawn chance (from 1 to x), and max spawn amount
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    playerInventory = gameData.get("PlayerInventory")

    if random.randint(1, spawnChance) == 1:
        spawnAmount = random.randint(1, maxSpawnAmount)
        print(f"You got {spawnAmount} {itemName}")

        # .get() can give existing amount, or 0 if it doesn't exist yet
        playerInventory[itemName] = playerInventory.get(itemName, 0) + spawnAmount

    with open("data.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)


def Mine():
    Aquire("coal", 1, 4)
    Aquire("iron", 2, 4)
    Aquire("silver", 3, 3)
    Aquire("gold", 4, 3)
    Aquire("diamond", 10, 2)


def Gather():
    Aquire("wood", 1, 4)
    Aquire("berries", 1, 3)
    Aquire("fruit", 2, 3)
    Aquire("mysterious potion", 5, 2)
    Aquire("mysterious blade", 100, 1)


def Rest():
    # Define player statistics
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    playerData = gameData.get("PlayerData")
    playerCondition = playerData.get("PlayerCondition")

    currentHealth = playerCondition.get("Health")
    maxHealth = playerCondition.get("MaxHealth")
    healAmount = int(maxHealth * 0.15) # +15% health

    # Limit healAmount if currentHealth will exceed maxHealth with healAmount
    if currentHealth + healAmount > maxHealth:
        healAmount = maxHealth - currentHealth

    # Heal player
    currentHealth += healAmount
    if currentHealth > maxHealth:
        currentHealth = maxHealth

    print(f"You regenerated {healAmount} health.\nYou now have {currentHealth} HP.")

    # Save player health
    playerCondition["Health"] = currentHealth

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii = False)

def Shop():
    pass


def Main():
    while True:
        action = str(input("\nWhat would you like to do?\n> ")).lower()
        print()

        match action:
            case "quit":
                break
            case "adventure":
                Adventure()
            case "mine":
                Mine()
            case "gather":
                Gather()
            case "rest":
                Rest()
            case "shop":
                Shop()
            case "restart":
                Restart()
            case _:
                print("Invalid action")
                continue


if __name__ == "__main__":
    Main()