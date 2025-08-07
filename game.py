import random
from player import Player
"""

cc = community cards

do we need card class?
"""

player_names = ['Raj', 'Jay', 'Kasra', 'Scott', 'Ethan']

class Game:

    def __init__(self, players):
        self.players = [Player(name) for name in player_names]
        self.deck = self.create_deck()
        self.cc = []
        self.states = ['pf', 'f', 't', 'r', 's']
        self.state_idx = 0
        self.dealer_idx = 0
        self.pot = 0

    def create_deck(self):
        suits = ["diamonds", "hearts", "spades", "clubs"]
        rank = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

        deck = [f"{r} of {s}" for s in suits for r in rank] 
        random.shuffle(deck)

        return deck
    
    def shift_roles(self):
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        self.sb_idx = (self.dealer_idx + 1) % len(self.players)
        self.bb_idx = (self.dealer_idx + 2) % len(self.players)
        pass

    def deal_cards(self):
        for _ in range(2):
            for player in self.players:
                player.get_card(self.deck.pop())

    def deal_cc(self):
        if self.states[self.state_idx] == 'f':
            self.deck.pop()
            self.cc.extend([self.deck.pop() for _ in range(3)])
            print(self.cc)
        elif self.states[self.state_idx] in ['t', 'r']:
            self.deck.pop()
            self.cc.append(self.deck.pop())
            print(self.cc)
        
    def betting_round(self, fta):
        player_idx = fta
        current_bet = 0
        betting_done = False
        last_raiser_idx = fta
        to_call = 0
        is_fta = True


        while not betting_done:
            print(f"Current Pot: {self.pot}")
            player = self.players[player_idx]

            if player_idx == last_raiser_idx:
                if is_fta:
                    is_fta = False
                else:    
                    betting_done = True
                    continue


            if player.folded or player.chips == 0:
                player_idx = (player_idx + 1) % len(self.players)
                continue

            to_call = current_bet - player.current_bet
            print(f"{player.name}'s turn\n")
            print(f"Chips: {player.chips}, Current Bet: {player.current_bet}")
            print(f"Call: {current_bet - player.current_bet}")
            

            # show player options
            if to_call > 0:
                action = input(f"Hey {player.name}, choose (fold, call, raise, all in):").strip().lower()
            else:
                action = input(f"choose action (check, bet, all in)").strip().lower()

            if action == "fold":
                player.folded = True
                print(f"{player.name} folded like a lil bish")

            elif action == "check" and to_call == 0:
                print(f"{player.name} checked")

            elif action == "call" and to_call > 0:
                if player.chips >= to_call:
                    player.chips -= to_call
                    player.current_bet += to_call
                    self.pot += to_call
                    print(f"{player.name} calls")
                else:
                    print(f"{player.name} goes all in with {player.chips} !!")
                    player.current_bet += player.chips
                    self.pot += player.chips
                    player.chips = 0
            
            elif action == "bet" and to_call == 0:
                # deal with non ints and 
                valid_bet = False
                while not valid_bet:
                    try:
                        amount = abs(int(input("Put in a bet size plz")))
                        valid_bet = True
                    except Exception as e:
                        print(f"you fucking tard you need to put an integer number")
                if 0 < amount <= player.chips:
                    player.chips -= amount
                    player.current_bet = amount
                    self.pot += amount
                    current_bet = amount
                    last_raiser_idx = player_idx
                    print(f"{player.name} bets {amount}!")
                else:
                    print("how did we get this should be impops")
                
            elif action == "raise" and to_call > 0:
                valid_bet = False
                while not valid_bet:
                    try:
                        amount = abs(int(input("Enter Raise Amount")))
                        valid_bet = True
                    except Exception as e:
                        print(f"you fucking tard you need to put an integer number")

                if amount > current_bet and amount <= player.current_bet + player.chips:
                    diff = amount - player.current_bet
                    player.chips -= diff
                    player.current_bet = amount
                    self.pot += diff
                    current_bet = amount
                    last_raiser_idx = player_idx
                    print(f"{player.name} raised to {amount}")
                else:
                    print("how did you get here")
                
            elif action == "all-in":
                amount = player.chips
                player.current_bet += amount
                self.pot += amount
                player.chips = 0

                if player.current_bet > current_bet:
                    current_bet = player.current_bet
                    last_raiser_idx = player_idx
                    
                print(f"{player.name} goes all in with {amount}")
            
            else:
                print("bad wrong bad boy put action that exist dummy")
                continue

            player_idx = (player_idx + 1) % len(self.players)




    def play_round(self):
        phase = self.states[self.state_idx]
        
        print(f"we are in {phase} of the game")

        if phase == 'pf':
            self.deal_cards()
            fta = (self.dealer_idx + 3) % len(self.players)
        elif phase in ['f', 't', 'r']:
            self.deal_cc()
            fta = (self.dealer_idx + 1) % len(self.players)
        else:
            self.showdown()
            
        # betting round fucntin
        if phase != 's':
            self.betting_round(fta)

        self.state_idx += 1

    def showdown(self):
        
        print("End of round")
        return

    def start_game(self):
        self.deck = self.create_deck()
        self.cc = []
        self.state_idx = 0
        self.pot = 0
        
        for player in self.players:
            player.reset_hand()

        # self.shift_roles()
        while self.states[self.state_idx] != 's':
            self.play_round()
        print("Showdown")
