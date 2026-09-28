kenteken = input("License: ")

vorm = ""

if kenteken[0] == "-":
    vorm = vorm + "-"
else:
    if kenteken[0].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[1] == "-":
    vorm = vorm + "-"
else:
    if kenteken[1].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[2] == "-":
    vorm = vorm + "-"
else:
    if kenteken[2].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[3] == "-":
    vorm = vorm + "-"
else:
    if kenteken[3].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[4] == "-":
    vorm = vorm + "-"
else:
    if kenteken[4].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[5] == "-":
    vorm = vorm + "-"
else:
    if kenteken[5].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[6] == "-":
    vorm = vorm + "-"
else:
    if kenteken[6].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if kenteken[7] == "-":
    vorm = vorm + "-"
else:
    if kenteken[7].isdigit():
        vorm = vorm + "9"
    else:
        vorm = vorm + "X"

if vorm == "XX-99-99" or vorm == "99-99-XX" or vorm == "99-XX-99" or vorm == "XX-99-XX" or vorm == "XX-XX-99" or vorm == "99-XX-XX" or vorm == "99-XXX-9" or vorm == "9-XXX-99" or vorm == "XX-999-X" or vorm == "X-999-XX" or vorm == "XXX-99-X" or vorm == "9-XX-999":
    print("Valid")
else:
    print("Invalid")