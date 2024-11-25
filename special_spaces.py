class Space:
    def __init__(self, name: str):
        self.name = name

    def display_info(self):
        print(f"Space: {self.name}")


class NonPropertySpace(Space):
    def __init__(self, name: str, description: str, action: str):
        super().__init__(name)
        self.description = description
        self.action = action

    def display_info(self):
        print(f"Non-Property Space: {self.name}")
        print(f"Description: {self.description}")
        print(f"Action: {self.action}")
