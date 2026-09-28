import random
import json

def Setup():
    global gameData
    global playerData

    # Open json file and define gameData from json data
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    # define playerData
    playerData = gameData.get("PlayerData")


def DiceRoll():
    return random.randint(1, 20)

#region Combat

def Combat(monsterName, enemyClass):
    enemyData = gameData.get("MonsterData")[enemyClass][monsterName]
    monsterHealth = enemyData.get("Health")
    monsterDamage = enemyData.get("Damage")

    # Open json file and define gameData from json data
    with open("data.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    # define playerData
    playerData = gameData.get("PlayerData")

    while playerHealth > 0 or monsterHealth > 0:
        match str(input(f"How would you like to attack?\n{playerData.get("Skills")}\n> ")).lower():
            case "attack":
                monsterHealth -= playerData.get("Strength")
                print(f"\nYou did {playerData.get("Strength")} damage!\nThe {monsterName} has {monsterHealth} HP left!\n")
            case "heal":
                playerHealth += 20
                print(f"\nYou healed 20 HP!\nYou have {playerHealth} HP left!\n")

        if monsterHealth > 0:
            playerHealth -= monsterDamage
            print(f"The {monsterName} did {monsterDamage} damage!\nYou have {playerHealth} HP left!\n")
        else:
            print(f"You defeated the {monsterName}!\nYou gained x XP!\n")
            break

    with open("FantasyGame.json", "w", encoding="utf-8") as f:
        json.dump(gameData, f, indent=4, ensure_ascii=False)


def Adventure():
    # Gabriël
    monsterData = gameData.get("MonsterData")

    if playerData.get("Intelligence") > 0:
        monsterName = random.choice(list(monsterData["Monsters"].keys()))
        print(f"\nYou encountered a {monsterName}")
        Combat(monsterName, "Monsters")
    else:
        print("You encountered nothing\n")

#endregion

#region Gathering

def Mine():
    #When mining give the player a random ore based on rarity and random amount from 1 to 4 
    coal = random.randint(1, 4)
    print(f"You got {coal} coal(s)")
    silver = random.randint(1, 3)
    if silver >= 2:
        silveramount = random.randint(1, 3)
        print(f"You got {silveramount} silver(s)")
    gold = random.randint(1, 2)
    if gold == 2:
        goldamount = random.randint(1, 2)
        print(f"You got {goldamount} gold(s)")
    iron = random.randint(1, 4)
    if iron >= 2:
        ironamount = random.randint(1, 4)
        print(f"You got {ironamount} iron(s)")
    diamond = random.randint(1, 5)
    if diamond == 5:
        diamondamount = random.randint(1, 2)
        print(f"You got {diamondamount} diamond(s)")

def Gather():
    #When gathering give the player a random item from a list of items based on rarity and random amount from 1 to 4
    item = random.choice(["Wood", "Berries", "Fruit", "Random blade", "Mysteryious potion"])
    wood = random.randint(1, 4)
    print(f"You got {wood} wood(s)")
    berries = random.randint(1, 3)
    if berries >= 2:
        berriesamount = random.randint(1, 2)
        print(f"You got {berriesamount} berries(s)")
    fruit = random.randint(1, 2)
    if fruit == 2:
        fruitamount = random.randint(1, 2)
        print(f"You got {fruitamount} fruit(s)")
    mysterious_potion = random.randint(1, 5)
    if mysterious_potion == 5:
        mysterious_potionamount = random.randint(1, 2)
        print(f"You got {mysterious_potionamount} mysterious potion(s)")
    mystery_blade_chance = random.randint(1, 100)
    if mystery_blade_chance == 100:
        mystery_blade = 1
        print(f"You got the mysterious blade! (1/100 chance)")

#endregion

def Rest():
    #when resting regenarate 15% of max health and dont let them go above their max hp
    currentHealth = playerData.get("Health")
    maxHealth = playerData.get("MaxHealth")
    regeneratedHealth = int(maxHealth * 0.15)

    currentHealth += regeneratedHealth
    if currentHealth > maxHealth:
        currentHealth = maxHealth

    if currentHealth + regeneratedHealth > maxHealth:
        regeneratedHealth = maxHealth - currentHealth

    currentHealth += regeneratedHealth
    print(f"You regenerated {regeneratedHealth} health.\nYou now have {currentHealth} HP.")

    with open("FantasyGame.json", "w", encoding="utf-8") as f:
        json.dump(gameData, f, indent=4, ensure_ascii=False)

def Shop():
    # Gabriël
    pass


def Main():
    Setup()

    while True:
        match str(input("What would you like to do?\n> ")).lower():
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
            case _:
                print("Invalid action")
                continue

Main()