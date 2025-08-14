import random
from player import Player
from card import Card
from itertools import combinations
from eval import get_best_hand
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

hand_names = {
    9: "Straight Flush",
    8: "Four of a kind",
    7: "Full House",
    6: "Flush",
    5: "Straight",
    4: "Three of a Kind",
    3: "Two Pair",
    2: "One Pair",
    1: "High Card"
}

def hand_name(key):
    category = hand_names[key[0]]
    if key[0] == 9 and key[1] == 14:
        return "Royal Flush"
    return category


class Game:

    def __init__(self, players, small_blind, big_blind):
        self.players = [Player(name) for name in players]
        self.small_blind = small_blind
        self.big_blind = big_blind
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

    def post_blinds(self):
        sb_player = self.players[self.sb_idx]
        bb_player = self.players[self.bb_idx]

        for player in self.players:
            player.current_bet = 0
        
        self.put_in_pot(sb_player, self.small_blind)
        self.put_in_pot(bb_player, self.big_blind)

    def put_in_pot(self, player, amount):
        if amount <= 0:
            return
        take = min(amount, player.chips)
        player.chips -= take
        player.current_bet += take
        player.committed += take
        self.pot += take
    
    def build_side_pots(self):
        contrib = {player: player.committed for player in self.players if not player.folded and player.committed > 0}
        pots = []

        while contrib:
            contributors = list(contrib.keys())
            min_amount = min(contrib.values())
            pot_amount = min_amount * len(contributors)
            pots.append({"amount": pot_amount, "eligible": contributors[:]})

            new_contrib = {}
            for player, amount in contrib.items():
                remaining = amount - min_amount
                if remaining > 0:
                    new_contrib[player] = remaining
            contrib = new_contrib

        return pots
        
    def betting_round(self, fta, phase):
        
        player_idx = fta

        if phase == 'pf':
            current_bet = self.big_blind
            last_raise_size = self.big_blind
            last_raiser_idx = self.bb_idx
        else:
            current_bet = 0
            last_raise_size = 0
            last_raiser_idx = None
        
        saw_aggression = False

        def next_eligible(i):
            j = (i + 1) % len(self.players)
            while self.players[j].folded or self.players[j].chips == 0:
                j = (j + 1) % len(self.players)
                if j == i:
                    break
            return j
        
        while self.players[player_idx].folded or self.players[player_idx].chips == 0:
            player_idx = next_eligible(player_idx)

        checks_in_row = 0

        while True:
            
            still_in = [player for player in self.players if not player.folded]

            if len(still_in) == 1:
                w = still_in[0]
                print(f"{w.name} wins pot")
                w.chips += self.pot
                self.pot = 0
                for player in self.players:
                    player.committed = 0
                self.state_idx = len(self.states) - 1
                return

            player = self.players[player_idx]
            if player.folded or player.chips == 0:
                player_idx = next_eligible(player_idx)
                continue

            to_call = current_bet - player.current_bet
            print(f"\n Current Pot: {self.pot}")
            print(player)
            print(f"{player.name}'s turn")
            print(f"Chips: {player.chips}, Current bet: {player.current_bet}, Call {to_call}")

            if to_call > 0:

                min_raise = last_raise_size if last_raise_size > 0 else (self.big_blind if phase == "pf" else 1)
                can_call = player.chips >= to_call
                can_raise = player.chips >= (to_call + min_raise)
                if can_call and can_raise:
                    valid_actions = ["fold", "call", "raise", "all-in"]
                elif can_call:
                    valid_actions = ["fold", "call", "all-in"]
                else:
                    # short stacked -> probably finna shove lmao
                    valid_actions = ["fold", "all-in"]
            else:
                valid_actions = ["fold", "check", "bet", "all-in"]
            
            action = input(f"{player.name}, choose action ({','.join(valid_actions)}) ").strip().lower()

            if action not in valid_actions:
                print("Invalid action, Try again")
                continue

            if action == "fold":
                player.folded = True
                checks_in_row = 0
                print(f"{player.name} folded")

            elif action == "check":
                if to_call > 0:
                    print("Can't check there is a bet")
                    continue
                checks_in_row += 1
                print(f"{player.name} checks")

            elif action == "call":
                self.put_in_pot(player, to_call)
                checks_in_row = 0
                print(f"{player.name} calls {to_call}")

            elif action == "bet":
                while True:
                    try:
                        amount = int(input("Enter bet amount: "))
                        if amount <= 0 or amount > player.chips:
                            print("Invalid bet amount")
                            continue
                        break
                    except:
                        print("Enter a valid number within your stack amount")
                self.put_in_pot(player, amount)
                current_bet = amount
                last_raise_size = amount
                last_raiser_idx = player_idx
                saw_aggression = True
                checks_in_row = 0
                print(f"{player.name} bets {amount}")

            elif action == "raise":
                if last_raise_size == 0:
                    last_raise_size = self.big_blind if phase == 'pf' else (current_bet if current_bet > 0 else 1)
                
                min_raise_to = current_bet + last_raise_size

                while True:
                    try:
                        amount = int(input(f"Enter an amount to raise to: (min raise {min_raise_to}) "))
                        raise_amount = amount - current_bet
                        if amount <= current_bet:
                            print("Raise must exceed current bet")
                            continue
                        if raise_amount < last_raise_size:
                            print(f"Raise must be {last_raise_size} more than current bet")
                            continue
                        if amount > player.current_bet + player.chips:
                            print("You don't have enough chips for that raise")
                            continue
                        break
                    except:
                        print("Enter a valid number")
                
                diff = amount - player.current_bet
                self.put_in_pot(player, diff)
                current_bet = amount
                last_raise_size = raise_amount
                last_raiser_idx = player_idx
                saw_aggression = True
                checks_in_row = 0
                print(f"{player.name} raises to {amount}")


            elif action == "all-in":
                amt = player.chips
                self.put_in_pot(player, amt)
                new_bet = player.current_bet

                if new_bet > current_bet:
                    raise_amount = new_bet - current_bet
                    min_inc = last_raise_size if last_raise_size > 0 else (self.big_blind if phase == 'pf' else 1)

                    if raise_amount >= min_inc:
                        # Full all-in raise → reopens action
                        current_bet = new_bet
                        last_raise_size = raise_amount
                        last_raiser_idx = player_idx
                        saw_aggression = True
                    else:
                        # Short all-in raise → price increases, but action does NOT reopen
                        current_bet = new_bet
                checks_in_row = 0
                print(f"{player.name} goes all-in for {amt}")


            #ending logic portion

            if current_bet > 0:
                can_act = any(
                    (not pl.folded) and (pl.current_bet < current_bet) and (pl.chips > 0)
                    for pl in self.players
                )
                if not can_act:
                    # pf case
                    if phase == 'pf' and last_raiser_idx is not None:
                        nxt = next_eligible(player_idx)
                        lr = self.players[last_raiser_idx]
                        if nxt == last_raiser_idx and not lr.folded:
                            player_idx = last_raiser_idx
                            continue
                    break

            if current_bet == 0:
                eligible_count = sum(1 for p in self.players if (not p.folded) and (p.chips > 0))
                if eligible_count == 0:
                    break
                if checks_in_row >= eligible_count:
                    break

            # Next player
            player_idx = next_eligible(player_idx)

    def play_round(self):
        phase = self.states[self.state_idx]
        print(f"we are in {phase} of the game")

        if phase == 'pf':
            self.deal_cards()
            self.post_blinds()
            fta = (self.dealer_idx + 3) % len(self.players)
        elif phase in ['f', 't', 'r']:
            self.deal_cc()
            fta = (self.dealer_idx + 1) % len(self.players)
        
        for player in self.players:
            if phase != "pf":
                player.current_bet = 0

        self.betting_round(fta, phase)
        self.state_idx += 1

    def showdown(self):
        pots = self.build_side_pots()
        if not pots:
            print("No chips in pot")
            return
        
        best_cache = {}
        for p in self.players:
            if p.folded:
                continue
            key, best5 = get_best_hand(p.hand, self.cc)
            best_cache[p] = (key, best5)
            pretty = " ".join(str(c) for c in best5)
            print(f"{p.name}'s best hand: {pretty} -> {hand_name(key)} {key}")

        # Award each pot separately
        for i, pot in enumerate(pots):
            elig = [p for p in pot["eligible"] if not p.folded]
            if not elig:
                continue
            # Find best among elig
            best_key = None
            winners = []
            for p in elig:
                key, _ = best_cache[p]
                if best_key is None or key > best_key:
                    best_key = key
                    winners = [p]
                elif key == best_key:
                    winners.append(p)
            # Split amount
            amount = pot["amount"]
            share = amount // len(winners)
            rem = amount % len(winners)
            for idx, w in enumerate(winners):
                payout = share + (1 if idx < rem else 0)
                w.chips += payout
            names = ", ".join(w.name for w in winners)
            print(f"Pot {i+1}: {amount} chips -> {names} win(s) {share} each{' +1' if rem else ''}")

        # Clear pot and contributions
        self.pot = 0
        for p in self.players:
            p.committed = 0

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
        
