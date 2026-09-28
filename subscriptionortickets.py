def validate_float(a:str) -> bool:
    try:
        float(a)
        return True
    except ValueError:
        return False
def validate_int(a:str) -> bool:
    try:
        int(a)
        return True
    except ValueError:
        return False


subscription = input("Vul hier de prijs in van de subscription: ")
single_ticket_price = input("Vul hier de prijs in van een ticket: ")
visits = input("Hoe vaak ga je: ")

if not validate_float(subscription) or not validate_float(single_ticket_price) or not validate_int(visits):
    print("Invalid input")
else:
    subscription = float(subscription)
    single_ticket_price = float(single_ticket_price)
    visits = int(visits)
    
    single_tickets = single_ticket_price * visits
    if single_tickets == subscription:
        print(f"Single tickets: €{single_tickets} Monthly subscription: €{subscription}  Advice: Buy single tickets")
    
    elif single_tickets <= subscription:
        print(f"Single tickets: €{single_tickets} Monthly subscription: €{subscription} Advice: Buy single tickets")
    
    elif single_tickets >= subscription:
        print(f"Single tickets: €{single_tickets} Monthly subscription: €{subscription}  Advice: buy a subscription")
        print(f"You save €{single_tickets - subscription}")