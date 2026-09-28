import random
import json

def Setup():
    global gameData
    global playerData

    # Open json file and define gameData from json data
    with open("stats.json", "r", encoding = "utf-8") as f:
        gameData = json.load(f)

    # define playerData
    playerData = gameData.get("PlayerData")

    # Open json file and dump gameData into json file
    with open("stats.json", "w", encoding = "utf-8") as f:
        json.dump(gameData, f, indent = 4, ensure_ascii=False)


def DiceRoll():
    return random.randint(1, 20)


def Combat():
    # Gabriël
    pass


def Adventure(skill):
    # Gabriël
    if DiceRoll() < playerData.get(skill):
        print("You encountered a monster")
        Combat()
    else:
        print("No monster")


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
                Adventure("Strength")
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