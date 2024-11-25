from player import Player
from property import Property
from special_spaces import Space, NonPropertySpace
from utils import roll_dice

def test_dice_roll():
    for _ in range(1):
        roll_dice()

if __name__ == "__main__":
    test_dice_roll()
def test_player_class():
    # Create a player
    player1 = Player("Cam", 1500)

    # Move the player
    player1.move(7, 40)  # Assuming a board with 40 spaces

    # Adjust money
    player1.adjust_money(+200)  # Deduct $200

    # Buy a property
    player1.buy_property("Broadway", 200)

    # Display player status
    player1.display_status()

def test_property_class():
    # Create a player
    player1 = Player("Cam", 1500)

    # Create a property
    broadway = Property("Broadway", 200, 50)

    # Display property status
    broadway.display_status()

    # Player purchases the property
    broadway.purchase(player1)

    # Improve the property
    broadway.improve(100)

    # Display updated property status
    broadway.display_status()


def test_space_classes():
    # Create a generic space
    space = Space("Generic Space")
    space.display_info()

    # Create a non-property space
    go = NonPropertySpace("Go", "Collect $200 as you pass.", "Collect $200")
    go.display_info()

if __name__ == "__main__":
    test_space_classes()

# Run the test
if __name__ == "__main__":
    test_property_class()