class Player:
    def __init__(self, name: str, money: int, position: int = 0, player_id=None):
        self.name = name
        self.money = money
        self.position = position
        self.player_id = player_id
        self.properties = []  # List of properties owned by the player

    def move(self, steps: int, board_size: int):
        # how the player moves
        self.position = (self.position + steps) % board_size
        print(f"{self.name} moved to position {self.position}.")

    def adjust_money(self, amount: int):
        self.money += amount
        print(f"{self.name}'s money is now ${self.money}.")

    def buy_property(self, property_name: str, cost: int):
        #how the player buys property
        if self.money >= cost:
            self.money -= cost
            self.properties.append(property_name)
            print(f"{self.name} bought {property_name} for ${cost}.")
        else:
            print(f"{self.name} cannot afford {property_name}.")

    def display_status(self):
        print(f"Player: {self.name}")
        print(f"Money: ${self.money}")
        print(f"Position: {self.position}")
        print(f"Properties: {', '.join(self.properties) if self.properties else 'None'}")
