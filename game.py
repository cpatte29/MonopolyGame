from database import  (insert_player, get_all_players, insert_player, load_player_from_DB, create_tables,
insert_property, insert_nonproperty, update_player, update_property)
from property import Property
from player import Player
from special_spaces import Space, NonPropertySpace
from utils import roll_dice
from gameboard import GameBoard
from connection import create_connection
from monopoly_data import monopoly_properties, monopoly_special_spaces
# Assuming GameBoard and player objects exist
def player_turn(player, board): # movement for player
    print(f"{player.name}'s turn.")
    steps = roll_dice()
    player.move(steps, board.size)
    board.interact_with_space(player, player.position)

class Game:
    def __init__(self):
        #Initializes the game state.
        self.players = []
        self.properties = []
        self.spaces = []
        self.starting_money = None
        self.board = None
        self.current_player = None

    def setup_game(self):
        #Sets up the game board by combining properties and spaces into the board. Makes sure that (players, properties, spaces) are added.
        # Validate game components
        if not self.players or not self.properties or not self.spaces:
            print("Please add players, properties, and spaces before setting up the game.")
            return False

        # Convert players from dictionaries
        self.players = [
            Player(name=player["name"], money=player["money"])
            if isinstance(player, dict) else player
            for player in self.players
        ]

        # Combine properties and spaces into the game board
        board_spaces = self.properties + self.spaces
        self.board = GameBoard(board_spaces)

        print("Game board setup complete!")
        return True

    def play_game(self, connection):
        #Starts the game loop if setup is complete. MUST SET up game before play game
        if not self.setup_game():
            print("Setup incomplete. Please complete all steps before starting the game.")
            return

        print("Game setup complete! Starting the game...")
        self.current_turn = 0

        while True:
            current_player = self.players[self.current_turn]
            print(f"\n{current_player.name}'s turn!")

            # Roll dice
            steps = roll_dice()

            # Move player
            current_player.move(steps, self.board.size)

            # Interact with space
            self.board.interact_with_space(current_player, current_player.position, self.players, connection)

            # End game if a condition is met (e.g., a player is bankrupt)
            if current_player.money <= 0:
                self.sell_properties_to_bank(current_player, connection)
                if current_player.money <= 0:
                    print(f'{current_player.name} is bankrupt! and eliminated from the game')
                    self.players.remove(current_player)
                    if len(self.players) == 1:
                        print(f'{self.players[0].name} wins the game!')
                        break
                    continue
                print(f"{current_player.name} is bankrupt! Game over!")
                break

            # Rotate to the next player
            self.current_turn = (self.current_turn + 1) % len(self.players)

    def sell_properties_to_bank(self, player, connection):
        # allows in game for players to sell properties back to the bank
        print(f"{player.name} has $0 and must sell their properties back to the bank.")
        for prop in self.properties:
            if prop.owner == player.name:
                # Mark the property as unowned
                prop.owner = None
                prop.improvements = 0  # Reset improvements

                # Update the property in the database
                update_property(
                    connection,
                    property_id=prop.property_id,
                    owner_id=None,
                    improvements=0
                )
                print(f"{prop.name} has been sold back to the bank.")

    def save_game(self, connection):
        #a save game, inserts player names, properties and spaces without duplicating
        print("Saving game state...")

        # Save players
        for turn_order, player in enumerate(self.players):
            if not player.player_id:
                player.player_id = insert_player(
                    connection,
                    name=player.name,
                    money=player.money,
                    position=player.position,
                    turn_order=turn_order,  # This is calculated here
                )
            else:
                update_player(
                    connection,
                    player_id=player.player_id,
                    name=player.name,
                    money=player.money,
                    position=player.position,
                    turn_order=turn_order,

                )


        # Save properties
        for property in self.properties:
            # Convert owner name to owner_id
            owner_id = next((p.player_id for p in self.players if p.name == property.owner), None)

            if not property.property_id:  # If the property doesn't have a property_id, insert it
                property.property_id = insert_property(
                    connection,
                    name=property.name,
                    cost=property.cost,
                    base_rent=property.base_rent,
                    owner_id=owner_id,  # Use owner_id from players
                    improvements=property.improvements  # Save improvement count
                )
            else:  # Otherwise, update the existing property
                update_property(
                    connection,
                    property_id=property.property_id,  # Use existing property_id
                    owner_id=owner_id,  # Update owner_id if changed
                    improvements=property.improvements  # Update improvements
                )

        # Save non-property spaces
        for space in self.spaces:
            if isinstance(space, NonPropertySpace):
                insert_nonproperty(
                    connection,
                    name=space.name,
                    description=space.description,
                    action=space.action
                )

        print("Game state saved successfully!")


def prompt_add_players():
    # a option to add players and money
    players = []
    print("Enter player details. Type 'done' when finished.")

    while True:
        name = input("Enter player name (or 'done' to finish): ").strip()
        if name.lower() == "done":
            break
        try:
            money = int(input(f"Enter starting money for {name}: ").strip())
            player = Player(name=name, money=money)  # Create a Player object
            players.append(player)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    print(f"Added players: {', '.join(player.name for player in players)}")
    return players

def prompt_add_properties(monopoly_properties):
    # adds properties by name, rent and cost
    # Flatten the nested list
    monopoly_properties = [item for sublist in monopoly_properties for item in sublist]

    properties = []
    print("Choose an option to add properties:")
    print("1. Use predefined Monopoly properties")
    print("2. Create your own custom properties")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print("\nAdding predefined Monopoly properties:")
        for prop in monopoly_properties: #goes through the predefined monopoly list
            property_obj = Property(prop["name"], prop["deed_cost"], prop["rent"])
            properties.append(property_obj)
            print(f"Added {prop['name']} (Cost: ${prop['deed_cost']}, Rent: ${prop['rent']})")
    elif choice == "2":
        print("\nEnter custom property details. Type 'done' when finished.")
        while True:
            name = input("Enter property name (or 'done' to finish): ").strip()
            if name.lower() == "done":
                break
            try:
                deed_cost = int(input(f"Enter the purchase cost for {name}: ").strip())
                rent = int(input(f"Enter the rent cost for {name}: ").strip())
                property_obj = Property(name, deed_cost, rent)
                properties.append(property_obj)
                print(f"Added {name} (Cost: ${deed_cost}, Rent: ${rent})")
            except ValueError:
                print("Invalid input. Please enter numeric values for cost and rent.")
    else:
        print("Invalid choice. Returning to the main menu.")

    return properties

def prompt_add_nonproperty_spaces(monopoly_special_spaces):
    #adds the spaces that are not properties
    spaces = []
    print("Choose an option to add special spaces:")
    print("1. Use predefined special spaces")
    print("2. Create your own special spaces")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print("\nAdding predefined special spaces:")
        for space in monopoly_special_spaces:
            space_obj = NonPropertySpace(space["name"], space["description"], space["action"])
            spaces.append(space_obj)
            print(f"Added {space['name']} - {space['description']}")
    elif choice == "2":
        print("\nEnter custom space details. Type 'done' when finished.")
        while True:
            name = input("Enter space name (or 'done' to finish): ").strip()
            if name.lower() == "done":
                break
            description = input(f"Enter a description for {name}: ").strip()
            action = input(f"Enter the action triggered by {name} (e.g., 'pay tax', 'draw card'): ").strip()
            space_obj = NonPropertySpace(name, description, action)
            spaces.append(space_obj)
            print(f"Added {name} - {description}")
    else:
        print("Invalid choice. Returning to the main menu.")

    return spaces


Welcome = "Welcome to the monopoly game!"
print(Welcome)
def handle_menu(game):
    # Displays the menu and handles user input to interact with the game.
    connection = create_connection()
    create_tables(connection)
    if not connection:
        print("Unable to connect to the database. Please try again.")
        return
    MENU_PROMPT = '''\nPlease choose an option below:
    1) Add players
    2) Add properties
    3) Add special spaces
    4) Set up the game
    5) Play game
    6) Save Game
    7) Exit Game
    Your selection: '''

    while (user_input := input(MENU_PROMPT)) != "7":
        if user_input == "1":
            game.players = prompt_add_players()
        elif user_input == "2":
            game.properties = prompt_add_properties(monopoly_properties)
        elif user_input == "3":
            game.spaces = prompt_add_nonproperty_spaces(monopoly_special_spaces)
        elif user_input == "4":
            game.setup_game()
        elif user_input == "5":
            game.play_game(connection)
        elif user_input == "6":
            game.save_game(connection)
        else:

            print("Invalid input. Please enter a valid number (1-6).")

    print("Exiting the game. Goodbye!")
    connection.close()

if __name__ == "__main__":
    print("Welcome to Monopoly!")
    monopoly_game = Game()
    handle_menu(monopoly_game)
if __name__ == "__main__":
    connection = create_connection()
    print("Database connection established:", connection)
    connection.close()
