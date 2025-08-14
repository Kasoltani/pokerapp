"""
Goal 1:
Deck of cards
shuffle cards
deal cards

"""
import random
from player import Player


def make_deck():

    suits = ["diamonds", "hearts", "spades", "clubs"]
    rank = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

    deck = [f"{r} of {s}" for s in suits for r in rank] 
    random.shuffle(deck)

    return deck

def game_loop(deck):


    game_state = ['pf', 'f', 't', 'r', 's']

    players = [Player("Jay"), Player("Raj")]

    for _ in range(2):
        for player in players:
            player.get_card(deck.pop())

    for player in players:
        print(player)


deck = make_deck()
game_loop(deck)