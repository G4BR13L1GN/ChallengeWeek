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

def Rest():
    #when resting regenarate 15% of max health and dont let them go above their max hp
    max_health = playerData.get("MaxHealth")
    current_health = playerData.get("Health")
    regened_health = float(max_health * 0.15)
    playerData["Health"] = min(current_health + regened_health)
    print(f"You regenerated {regened_health} health.")

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