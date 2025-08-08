# evaluator.py
import collections
from itertools import combinations

ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']

def is_straight(hand):
    sorted_ranks = sorted(set(ranks.index(card.rank) for card in hand))
    if len(sorted_ranks) < 5:
        return False
    return sorted_ranks[-1] - sorted_ranks[0] == 4 and len(sorted_ranks) == 5

def is_flush(hand):
    suits = [card.suit for card in hand]
    return len(set(suits)) == 1

def is_straight_flush(hand):
    return is_straight(hand) and is_flush(hand)

def is_four_of_a_kind(hand):
    counts = collections.Counter(card.rank for card in hand)
    return 4 in counts.values()

def is_full_house(hand):
    counts = collections.Counter(card.rank for card in hand).values()
    return 3 in counts and 2 in counts

def is_three_of_a_kind(hand):
    counts = collections.Counter(card.rank for card in hand)
    return 3 in counts.values()

def is_two_pair(hand):
    counts = collections.Counter(card.rank for card in hand)
    return list(counts.values()).count(2) == 2

def is_one_pair(hand):
    counts = collections.Counter(card.rank for card in hand)
    return list(counts.values()).count(2) == 1

def evaluate_hand_strength(hand):
    hand = sorted(hand, key=lambda c: ranks.index(c.rank))

    if is_straight_flush(hand): return 9
    if is_four_of_a_kind(hand): return 8
    if is_full_house(hand): return 7
    if is_flush(hand): return 6
    if is_straight(hand): return 5
    if is_three_of_a_kind(hand): return 4
    if is_two_pair(hand): return 3
    if is_one_pair(hand): return 2
    return 1  # High card

def get_best_hand(player_cards, community_cards):
    all_cards = player_cards + community_cards
    best_score = -1
    best_hand = None

    for combo in combinations(all_cards, 5):
        score = evaluate_hand_strength(combo)
        if score > best_score:
            best_score = score
            best_hand = combo
    return best_score, best_hand
