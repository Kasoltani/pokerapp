from itertools import combinations
from collections import Counter


ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
rank_values = {r: i+2 for i, r in enumerate(ranks)}

def values_desc(cards):
    return sorted((rank_values[c.rank] for c in cards), reverse=True)

def is_straight(vals_desc):
    vals = sorted(set(vals_desc), reverse=True)

    if len(vals) != 5:
        return (False, None)

    # wheel check
    if set(vals) == {14, 5, 4, 3, 2}:
        return (True, 5)

    # otherwise normal straight
    if vals[0] - vals[-1] == 4:
        return (True, vals[0])
    
    return (False, None)

def hand_rank(hand5):
    
    vals = [rank_values[c.rank] for c in hand5]
    vals_sorted = sorted(vals, reverse=True)
    counts = Counter(vals)
    count_and_val = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    # ^ [(val_quads,4), (kicker,1)] | [(val_trip,3), (val_pair, 2)]
    is_flush = (len({c.suit for c in hand5}) == 1)
    is_str, straight_high = is_straight(vals_sorted)

    if is_str and is_flush:
        return (9, straight_high)
    if count_and_val[0][1] == 4:
        #4 of a kind
        quad = count_and_val[0][0]
        kicker = count_and_val[1][0]
        return (8, quad, kicker)
    if count_and_val[0][1] == 3 and count_and_val[1][1] == 2:
        #full house
        trip = count_and_val[0][0]
        pair = count_and_val[1][0]
        return (7, trip, pair)
    if is_flush:
        return(6, *vals_sorted)
    if is_str:
        return(5, straight_high)
    if count_and_val[0][1] == 3:
        # trips
        trip = count_and_val[0][0]
        kickers = [v for v, c in count_and_val[1:] if c == 1]
        kickers.sort(reverse=True)
        return (4, trip, *kickers[:2])
    if count_and_val[0][1] == 2 and count_and_val[1][1] == 2:
        # two pair
        h_pair = max(count_and_val[0][0], count_and_val[1][0])
        l_pair = min(count_and_val[0][0], count_and_val[1][0])
        kicker = [v for v, c in count_and_val[2:] if c == 1]
        kicker_val = max(kicker) if kicker else 0
        return (3, h_pair, l_pair, kicker_val)
    if count_and_val[0][1] == 2:
        pair = count_and_val[0][0]
        kickers = [v for v, c in count_and_val[1:] if c == 1]
        kickers.sort(reverse=True)
        return (2, pair, *kickers[:3])
    return (1, *vals_sorted)

def get_best_hand(player_cards, community_cards):
    all_cards = player_cards + community_cards
    best_key = None
    best_hand = None
    for combo in combinations(all_cards, 5):
        key = hand_rank(combo)
        if best_key is None or key > best_key:
            best_key = key
            best_hand = combo
    return best_key, best_hand