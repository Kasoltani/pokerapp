import random
from player import Player
from card import Card
from itertools import combinations
from evaluator import get_best_hand, evaluate_hand_strength
"""
Notes:
cc = community cards

To-do:
do we need card class?
all-in logic
show hand to player
hand comparison find winner
choose to show hand
web-app integration
-> account - db - player creation
    -> two tables, user auth, players table
->routes for login logout playing
->buy domain
->host on some service


table logic
-> stand sit at table
-> join table with x chips
-> 7-2 logic
-> adding removing chips

"""


class Game:

    def __init__(self, players):
        self.players = [Player(name) for name in players]
        self.deck = self.create_deck()
        self.cc = []
        self.states = ['pf', 'f', 't', 'r', 's']
        self.state_idx = 0
        self.dealer_idx = 0
        self.pot = 0

    def create_deck(self):
        suits = ["H", "D", "C", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        deck = [Card(rank, suit) for suit in suits for rank in ranks] 
        random.shuffle(deck)

        return deck
    
    def shift_roles(self):
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        self.sb_idx = (self.dealer_idx + 1) % len(self.players)
        self.bb_idx = (self.dealer_idx + 2) % len(self.players)
        

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
        is_fta = True
        acted_players = set()


        while not betting_done:
            # edge if only one player remains
            not_folded = [player for player in self.players if not player.folded]
            if len(not_folded) == 1:
                print(f"{not_folded[0].name} wins pot uncontested")
                not_folded[0].chips += self.pot
                self.pot = 0
                return
            
            print(f"Current Pot: {self.pot}")
            player = self.players[player_idx]
            print(player)

            if player.folded or player.chips == 0:
                player_idx = (player_idx + 1) % len(self.players)
                continue

            to_call = current_bet - player.current_bet
            print(f"{player.name}'s turn\n")
            print(f"Chips: {player.chips}, Current Bet: {player.current_bet}\n")
            print(f"Call: {current_bet - player.current_bet}\n")
            

            # show player options
            if to_call > 0:
                valid_actions = ["fold", "call", "raise", "all-in"]
            else:
                valid_actions = ["fold", "check", "bet", "all-in"]
            
            action = input(f"{player.name}, choose action({','.join(valid_actions)}):").strip().lower()

            if action not in valid_actions:
                print("You didnt choose an action available")
                continue

            if action == "fold":
                player.folded = True
                print(f"{player.name} folded")

            elif action == "check":
                if to_call > 0:
                    print("Can't check there is a bet")
                    continue
                print(f"{player.name} checks")

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
            
            elif action == "bet":
                # deal with non ints and 
                while True:
                    try:
                        amount = int(input("Enter bet amount:"))
                        if amount <= 0 or amount > player.chips:
                            raise ValueError
                        else:
                            break
                    except:
                        print("Invalid bet")
                        continue

                current_bet = amount
                player.chips -= amount
                player.current_bet = amount
                self.pot += amount
                last_raiser_idx = player_idx
                print(f"{player.name} bet {amount}")
                
            elif action == "raise":
                while True:
                    try:
                        amount = int(input("Enter raise:"))
                        raise_amount = amount - player.current_bet
                        if raise_amount <= to_call or amount > player.chips + player.current_bet:
                            raise ValueError
                        else:
                            break
                    except:
                        print("Invalid raise")
                        continue

                diff = amount - player.current_bet
                player.chips -= diff
                player.current_bet = amount
                self.pot += diff
                current_bet = amount
                last_raiser_idx = player_idx
                print(f"{player.name} raised to {amount}")
                
            elif action == "all-in":
                amount = player.chips
                player.current_bet += amount
                self.pot += amount
                player.chips = 0

                if player.current_bet > current_bet:
                    current_bet = player.current_bet
                    last_raiser_idx = player_idx
                    
                print(f"{player.name} goes all in with {amount}")
            
            acted_players.add(player_idx)

            if player_idx == last_raiser_idx and not is_fta:
                break

            if len(acted_players) >= len([player for player in self.players if not player.folded and player.chips > 0]) and current_bet == 0:
                break

            is_fta = False

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
        
        for player in self.players:
            player.current_bet = 0
        self.betting_round(fta)

        self.state_idx += 1

    def showdown(self):
        best_score = -1
        winners = []

        for player in self.players:
            if player.folded:
                continue

            score, best_hand = get_best_hand(player.hand, self.cc)
            print(f"{player.name}'s best hand: {best_hand} with score {score}")

            if score > best_score:
                best_score = score
                winners = [player]
            elif score == best_score:
                winners.append(player)
            
        split_pot = self.pot // len(winners)
        for winner in winners:
            winner.chips += split_pot
            print(f"{winner.name} wins {split_pot} chips")
        self.pot = 0
        

    def start_hand(self):
        self.deck = self.create_deck()
        self.cc = []
        self.state_idx = 0
        self.pot = 0
        
        for player in self.players:
            player.reset_hand()

        while self.states[self.state_idx] != 's':
            self.play_round()
        
        self.showdown()

    def start_game_loop(self):
        while True:
            self.shift_roles()
            self.start_hand()

            for player in self.players:
                print(f"{player.name} has {player.chips} chips")
            
            cont = input("Next hand y/n:").lower()
            if cont != 'y':
                print("GGs")
                break
        
