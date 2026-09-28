import random
import json

def Setup():
    global gameData

    # Open json file and define gameData from json data
    with open("stats.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    # define playerData
    playerData = gameData.get("PlayerData")

    # Open json file and dump gameData into json file
    with open("stats.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii=False)


def Adventure():
    if random.randint(10) == 1:
        print("You encountered a monster")
    else:
        print(":)")


def DiceRoll(sides = int(20):
    return random.randint(1, sides)

def Main():
    Setup()

    while True:
        match str(input("What would you like to do?\n> ")).lower():
            case "quit":
                break
            case "adventure":
                Adventure()
            case _:
                print("Invalid action")
                continue