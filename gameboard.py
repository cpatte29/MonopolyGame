from special_spaces import Space, NonPropertySpace
from player import Player
from property import Property
import special_spaces
from database import update_property
from monopoly_data import monopoly_properties, monopoly_special_spaces, chance_cards
from utils import draw_chance_card, draw_community_chest_card
class GameBoard:
    def __init__(self, spaces):
        self.spaces = spaces
        self.size = len(spaces)  # Total number of spaces on the board

    def interact_with_space(self, player, position, players, connection):
        #how space interacts with the players
        space = self.get_space(position)

        if isinstance(space, Property):
            self.interact_with_property(player, space, players, connection)
        elif isinstance(space, NonPropertySpace):
            self.interact_with_nonproperty_space(player, players, space)

    def get_space(self, position):
        return self.spaces[position % self.size]

    def interact_with_property(self, player, property, players, connection):
        if property.owner is None:
            # If unowned, give the player the option to buy
            print(f"{player.name} can buy {property.name} for ${property.cost}.")
            choice = input(f"Do you want to buy {property.name}? (yes/no): ").strip().lower()
            if choice == "yes":
                if player.money >= property.cost:
                    player.money -= property.cost
                    property.owner = player.name
                    update_property(
                        connection,
                        property_id=property.property_id,
                        owner_id=player.player_id,
                        improvements=property.improvements
                    )
                    print(f"{player.name} purchased {property.name} for ${property.cost}.")
                    print(f"{property.owner} now has {player.money}.")
                else:
                    print(f"{player.name} does not have enough money to purchase {property.name}.")
        else:
            # If owned by another player, pay rent
            if property.owner != player.name:
                rent = property.calculate_rent()
                player.adjust_money(-rent)

                # Find the owner by name and update their money
                owner = next(p for p in players if p.name == property.owner)
                owner.adjust_money(rent)

                print(f"{player.name} pays ${rent} rent to {property.owner}.")
                print(f"{property.owner} now has ${owner.money}.")
            else:
                # If owned by the same player, offer an improvement option
                print(f"{player.name} landed on their own property, {property.name}.")
                choice = input(
                    f"Do you want to improve {property.name} for ${property.cost // 2}? (yes/no): ").strip().lower()
                if choice == "yes" and player.money >= property.cost // 2:
                    player.money -= property.cost // 2
                    property.improvements += 1
                    update_property(
                        connection,
                        property_id=property.property_id,
                        owner_id=player.player_id,
                        improvements=property.improvements
                    )
                    print(f"{property.name} has been improved. Total improvements: {property.improvements}.")
                    print(f"{property.owner} now has ${player.money}.")
                elif choice == "yes":
                    print(f"Not enough money to improve {property.name}.")

    def interact_with_nonproperty_space(self, player, players, space):
        print(f"{player.name} landed on {space.name}: {space.description}")
        if space.action == "collect_200":
            player.money += 200
            print(f"{player.name} collected $200!")
            print(f"{player.name} now has ${player.money}.")
        elif space.action == "pay_tax":
            tax = min(player.money // 10, 200)
            player.money -= tax
            print(f"{player.name} paid ${tax} in taxes.")
            print(f"{player.name} now has ${player.money}.")
        elif space.action == "pay_75":
            player.money -= 75
            print(f"{player.name} paid $75 for luxury tax.")
            print(f"{player.name} now has ${player.money}.")
        elif space.action == "jail":
            print(f"{player.name} is now in jail.")
        elif space.action == "draw_chance_card":
            draw_chance_card(player, players)
        elif space.action == "draw_community_chest_card":
            draw_community_chest_card(player, players, self)
        elif space.action == "no_action":
            print(f"{player.name} is just relaxing here.")
        else:
            print(f"No action defined for {space.name}.")

    def initialize_special_spaces(monopoly_special_spaces):
        return [
            NonPropertySpace(name=space["name"], description=space["description"], action=space["action"])
            for space in monopoly_special_spaces
        ]



