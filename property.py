from special_spaces import Space

class Property(Space):
    def __init__(self, name: str, cost: int, base_rent: int, property_id = None):
        super().__init__(name)# Initialize the Space base class
        self.cost = cost
        self.base_rent = base_rent
        self.owner = None  # Initially unowned
        self.improvements = 0  # Number of improvements (e.g., houses, hotels)
        self.property_id = property_id

    def calculate_rent(self) -> int:
        # Rent increases by 50% for each improvement
        return int(self.base_rent * (1 + 0.5 * self.improvements))

    def purchase(self, player):
        # how a property can get purchased
        if self.owner is None:
            if player.money >= self.cost:
                player.money -= self.cost
                self.owner = player.name
                player.properties.append(self.name)
                print(f"{player.name} purchased {self.name} for ${self.cost}.")
            else:
                print(f"{player.name} does not have enough money to purchase {self.name}.")
        else:
            print(f"{self.name} is already owned by {self.owner}.")

    def improve(self, improvement_cost: int):
        self.improvements += 1
        print(f"{self.name} has been improved. Total improvements: {self.improvements}.")

    def display_status(self):
        print(f"Property: {self.name}")
        print(f"Cost: ${self.cost}")
        print(f"Base Rent: ${self.base_rent}")
        print(f"Owner: {self.owner if self.owner else 'None'}")
        print(f"Improvements: {self.improvements}")
        print(f"Current Rent: ${self.calculate_rent()}")
