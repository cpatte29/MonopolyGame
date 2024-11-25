import random
from monopoly_data import chance_cards, community_chest_cards
def roll_dice() -> int:
    """Simulates the rolling of two six-sided dice.
    Returns:
        int: The total of the two dice rolls.
    """
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2
    print(f"Dice roll: {die1} + {die2} = {total}")
    return total

def draw_chance_card(player, players):
    card = random.choice(chance_cards)
    print(f"{player.name} drew a Chance card: {card['name']} - {card['description']}")

    if card["action"] == "pay_fine":
        player.money += card["amount"]
        print(f"{player.name} paid a fine of ${-card['amount']}. Remaining balance: ${player.money}.")
    elif card["action"] == "pay_each":
        total_paid = 0
        for other_player in players:
            if other_player != player:  # Skip the current player
                other_player.money += abs(card["amount"])
                total_paid += abs(card["amount"])
                print(f"{player.name} paid ${abs(card['amount'])} to {other_player.name}.")
        player.money += card["amount"] * len(players)  # Subtract total paid
        print(f"{player.name}'s remaining balance: ${player.money}.")
    elif card["action"] == "collect":
        player.money += card["amount"]
        print(f"{player.name} collected ${card['amount']}. New balance: ${player.money}.")
def draw_community_chest_card(player, players, board):
    card = random.choice(community_chest_cards)
    print(f"{player.name} drew a Community Chest card: {card['name']} - {card['description']}")

    if card["action"] == "advance_to_go":
        player.position = 0  # Assume 0 is the position for "Go"
        player.money += card["amount"]
        print(f"{player.name} advanced to Go and collected $200. New balance: ${player.money}.")
    elif card["action"] == "collect":
        player.money += card["amount"]
        print(f"{player.name} collected ${card['amount']}. New balance: ${player.money}.")
    elif card["action"] == "pay":
        player.money += card["amount"]  # Negative amount for payment
        print(f"{player.name} paid ${-card['amount']}. New balance: ${player.money}.")
    elif card["action"] == "birthday":
        total_collected = 0
        for other_player in players:
            if other_player != player:  # Exclude the current player
                other_player.money -= card["amount"]
                total_collected += card["amount"]
                print(f"{other_player.name} paid ${card['amount']} to {player.name}.")
        player.money += total_collected
        print(f"{player.name} collected ${total_collected} for their birthday. New balance: ${player.money}.")