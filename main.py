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


def Combat(monsterName, enemyType):
    enemyData = gameData.get("MonsterData")[enemyType][monsterName]
    monsterHealth = enemyData.get("Health")
    monsterDamage = enemyData.get("Damage")

    playerHealth = playerData.get("Health")

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
            print(f"You defeated the {monsterName}!\nYou gained x XP!")
            break

    with open("FantasyGame.json", "w", encoding="utf-8") as f:
        json.dump(gameData, f, indent=4, ensure_ascii=False)



def Adventure():
    # Gabriël
    monsterData = gameData.get("MonsterData")

    if playerData.get("Intelligence") > 0:
        monsterName = random.choice(list(monsterData["Bosses"].keys()))
        print(f"\nYou encountered a {monsterName}")
        Combat(monsterName, "Bosses")
    else:
        print("You encountered nothing\n")

def Mine():
    # Stojan
    pass


def Gather():
    # Stojan
    pass


def Rest():
    # Stojan
    pass


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