import string

def is_palindrome(tekst):
    schoon = ""
    for karakter in tekst:
        if karakter not in string.punctuation and karakter != " ":
            schoon += karakter.lower()

    links = 0
    rechts = len(schoon) - 1
    while links < rechts:
        if schoon[links] != schoon[rechts]:
            return False
        links += 1
        rechts -= 1
    return True

invoer = input("String: ")

if is_palindrome(invoer):
    print(f'"{invoer}" is a palindrome')
else:
    print(f'"{invoer}" is not a palindrome')