import random

def Adventure():
    pass

while True:
    match str(input("What would you like to do?\n> ")).lower():
        case "quit":
            break
        case "adventure":
            Adventure()
        case _:
            print("Invalid action")
            continue