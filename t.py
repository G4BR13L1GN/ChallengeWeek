from datetime import datetime

def is_first_name_valid(firstName):
        if firstName.isalpha() != True:
            return False
        elif len(firstName) < 2 or len(firstName) > 10:
            return False
        elif firstName[0].isupper() != True:
            return False
        else:
            return True

def is_last_name_valid(firstName):
        if firstName.isalpha() != True:
            return False
        elif len(firstName) < 2 or len(firstName) > 20:
            return False
        elif firstName[0].isupper() != True:
            return False
        else:
            return True

def is_start_time_valid(starttime):
    try:
        datetime.strptime(starttime, "%H:%M")
        return True
    except ValueError:
        return False

def is_end_time_valid(endtime):
    try:
        datetime.strptime(endtime, "%H:%M")
        return True
    except ValueError:
        return False
     

diffs = []

firstname = input("What is your first name: ")
while not is_first_name_valid(firstname):
    firstname = input("Invalid first name, try again: ")
lastname = input("What is your last name: ")
while not is_last_name_valid(firstname):
    firstname = input("Invalid last name, try again: ")
starttime = input("What was your start time in HH:MM format: ")
while not is_start_time_valid(starttime):
    starttime = input("Invalid start time, try again: ")
endtime = input("What was your end time in HH:MM format: ")
while not is_end_time_valid(endtime):
    endtime = input("Invalid end time, try again: ")


start = datetime.strptime(starttime, "%H:%M")
end = datetime.strptime(endtime, "%H:%M")

diff = end - start
print(diff)
diffs.append(diff)
average = len(diffs)
print(average)

x = "yes"

while x.lower() == "yes":
    x = input("Wil je verder gaan: Yes or No ")
    if x.lower() != "yes":
            break

    firstname = input("What is your first name: ")
    while not is_first_name_valid(firstname):
        firstname = input("Invalid first name, try again: ")
    lastname = input("What is your last name: ")
    while not is_last_name_valid(lastname):
        lastname = input("Invalid last name, try again: ")
    starttime = input("What was your start time in HH:MM format: ")
    while not is_start_time_valid(starttime):
        starttime = input("Invalid start time, try again: ")
    endtime = input("What was your end time in HH:MM format: ")
    while not is_end_time_valid(endtime):
        endtime = input("Invalid end time, try again: ")

    start = datetime.strptime(starttime, "%H:%M")
    end = datetime.strptime(endtime, "%H:%M")
    diff = end - start
    print(diff)
    diffs.append(diff)

total = diffs[0] * 0
for d in diffs:
    total += d

average = total / len(diffs)
participant_count = len(diffs)

print("Total participants:", participant_count)
print("Average time:", average)