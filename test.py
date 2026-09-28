def is_first_name_valid(name: str) -> bool:
    return (
        name.isalpha()
        and 2 <= len(name) <= 10
        and name[0].isupper()
    )
 
 
def is_last_name_valid(name: str) -> bool:
    allowed_characters = " ,-/"
    return (
        2 <= len(name) <= 20
        and all(character.isalpha() or character in allowed_characters for character in name)
        and any(character.isalpha() for character in name)
    )
 
 
def is_time_valid(time_str: str) -> bool:
    if len(time_str) != 5 or time_str[2] != ":":
        return False
    if not time_str[:2].isdigit() or not time_str[3:].isdigit():
        return False
 
    hours = int(time_str[:2])
    minutes = int(time_str[3:])
    return 0 <= hours <= 23 and 0 <= minutes <= 59
 
 
def time_to_minutes(time_str: str) -> int:
    return int(time_str[:2]) * 60 + int(time_str[3:])
 
 
def is_duration_valid(start: int, end: int) -> bool:
    duration = end - start
    return start < end and 10 <= duration <= 180
 
 
def minutes_to_time(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
 
 
def read_participant() -> tuple[str, str, int]:
    first_name = input("First name? ")
    while not is_first_name_valid(first_name):
        print("Input error")
        first_name = input("First name? ")
 
    last_name = input("Last name? ")
    while not is_last_name_valid(last_name):
        print("Input error")
        last_name = input("Last name? ")
 
    start_time = input("Start time? ")
    while not is_time_valid(start_time):
        print("Input error")
        start_time = input("Start time? ")
 
    end_time = input("Finish time? ")
    while True:
        if is_time_valid(end_time):
            start = time_to_minutes(start_time)
            end = time_to_minutes(end_time)
            if is_duration_valid(start, end):
                return first_name, last_name, end - start
 
        print("Input error")
        end_time = input("Finish time? ")
 
 
def main() -> None:
    total_time = 0
    participant_count = 0
    fastest_time = 0
    fastest_participant = ""
    new_participant = "Yes"
 
    while new_participant.lower() == "yes":
        first_name, last_name, duration = read_participant()
        participant_count += 1
        total_time += duration
 
        if participant_count == 1 or duration < fastest_time:
            fastest_time = duration
            fastest_participant = f"{first_name} {last_name}"
 
        average_time = total_time // participant_count
        if duration < average_time:
            comparison = "faster than"
        elif duration > average_time:
            comparison = "slower than"
        else:
            comparison = "as fast as"
        print(f"{first_name} {last_name} did it in {minutes_to_time(duration)}")
        print(f"This participant is currently {comparison} the average.")
 
        new_participant = input("New participant? (Yes or No): ")
        while new_participant.lower() not in ("yes", "no"):
            print("Input error")
            new_participant = input("New participant? (Yes or No): ")
 
    average_time = total_time // participant_count
    print(f"Fastest participant: {fastest_participant} ({minutes_to_time(fastest_time)})")
    print(f"Total participants: {participant_count}")
    print(f"Average time: {minutes_to_time(average_time)}")
 
 
if __name__ == "__main__":
    main()