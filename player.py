class Player:
    def __init__(self, name, chips=100):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False

    def fold(self):
        self.folded = True

    def bet(self, amount):
        if amount > self.chips:
            raise ValueError(f"{self.name} can't bet {amount}")
        self.chips -= amount
        self.current_bet += amount

    def get_card(self, card):
        self.hand.append(card)
        print(card)

    def reset_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False

    def __repr__(self):
        return f"{self.name}: Hand - {self.hand}, Chips - {self.chips}, Folded - {self.folded}"

