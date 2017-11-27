#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------


class JokerIterator:

    card = None

    TYPE_OF_CARD = {
        'B': ['C', 'S'],
        'R': ['H', 'D']
    }

    JOKER_SYMBOL = '?'

    def __init__(self, card):
        if card[Card.RANK_INDEX_IN_CARD] != self.JOKER_SYMBOL:
            raise Exception('Not a joker card')
        self.card = card

    def __iter__(self):
        cards = []
        for suit in self.TYPE_OF_CARD[self.card[Card.SUIT_INDEX_IN_CARD]]:
            suit_cards = []
            for rank in range(Card.MIN_RANK, Card.MAX_RANK+1):
                suit_cards.append(self.create_card(rank, suit))
            cards.extend(suit_cards)
        return iter(cards)

    def create_card(self, rank, suit):
        correct_rank = ''
        if rank in Card.RANKS_NUMERICAL.values():
            for rank_symbolic, rank_numerical in Card.RANKS_NUMERICAL.iteritems():
                if rank == rank_numerical:
                    correct_rank = rank_symbolic
                    break
        else:
            correct_rank = str(rank)
        return correct_rank + suit


class HandIterator:
    """ Итератор по всем возможным комбинациям в руке. """

    hand = None

    def __init__(self, hand):
        self.hand = hand

    def __iter__(self):
        combinantions = []
        indices_set = self.shuffle(0, Hand.CARDS_NUMBER_IN_HAND-1, Hand.CARDS_NUMBER_IN_COMBINATION)
        for indices in indices_set:
            combination = list(self.hand[i] for i in indices)
            combinantions.append(combination)
        return iter(combinantions)

    def shuffle(self, starting_index, max_index, number_of_indices):
        if number_of_indices == 1:
            return map(lambda x: [x], range(starting_index, max_index+1))
        indices = []
        for i in range(starting_index, max_index-number_of_indices+2):
            tails = self.shuffle(i+1, max_index, number_of_indices-1)
            for tail in tails:
                curr_arr = [i]
                curr_arr.extend(tail)
                indices.append(curr_arr)
        return indices

    def count_max_starting_index(self):
        return Hand.CARDS_NUMBER_IN_HAND - Hand.CARDS_NUMBER_IN_COMBINATION + 1


class Hand:
    """ Класс для работы с рукой карт. """
    cards = []

    CARDS_NUMBER_IN_HAND = 7
    CARDS_NUMBER_IN_COMBINATION = 5

    def __init__(self, card_strings):
        self.cards = list(map(lambda card_str: Card(card_str), card_strings))

    def get_ranks(self):
        return sorted(list(map(lambda card: card.rank, self.cards)))

    def get_suits(self):
        return sorted(list(map(lambda card: card.suit, self.cards)))


class Card:
    """ Класс с информацией по карте """

    rank = 0
    suit = ''

    RANKS_NUMERICAL = {
        'T': 10,
        'J': 11,
        'Q': 12,
        'K': 13,
        'A': 14
    }
    RANK_INDEX_IN_CARD = 0
    SUIT_INDEX_IN_CARD = 1
    CARD_LENGTH = 2
    MIN_RANK = 2
    MAX_RANK = 14
    SUITS = ['C', 'S', 'H', 'D']

    def __init__(self, card):
        if len(card) != self.CARD_LENGTH:
            raise Exception('Incorrect card format')
        self.rank = self.get_rank(card)
        self.suit = card[self.SUIT_INDEX_IN_CARD]
        if not self.is_correct():
            raise Exception('Incorrect card format')

    def get_rank(self, card):
        rank = card[self.RANK_INDEX_IN_CARD]
        if rank in self.RANKS_NUMERICAL:
            return self.RANKS_NUMERICAL[rank]
        return int(rank)

    def is_correct(self):
        return True
        # return (self.MIN_RANK <= self.rank <= self.MAX_RANK) and (self.suit in self.SUITS)




def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    return sorted(hand.get_ranks())


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    suits = hand.get_suits()
    first_suit = suits[0]
    for suit in suits[1:]:
        if suit != first_suit:
            return False
    return True


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    ranks = sorted(ranks)
    for i in range(0, len(ranks)-1):
        if ranks[i] != ranks[i+1] - 1:
            return False
    return True


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    ranks = sorted(ranks, reverse=True)
    for rank in ranks:
        if ranks.count(rank) == n:
            return rank
    return None


def check_rank_has_pair(rank, ranks):
    """ Есть ли у такого ранга пара. """
    return ranks.count(rank) >= 2


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    first_pair_rank = None
    for rank in ranks:
        if first_pair_rank is None and check_rank_has_pair(rank, ranks):
            first_pair_rank = rank
            continue
        if rank != first_pair_rank and check_rank_has_pair(rank, ranks):
            return first_pair_rank, rank
    return None


def count_best_combination_rank(hand):
    hand_iterator = HandIterator(hand)
    best_comination = []
    max_rank = 0
    for hand_combination in hand_iterator:
        hand = Hand(hand_combination)
        curr_rank = hand_rank(hand)
        if curr_rank > max_rank:
            max_rank = curr_rank
            best_comination = hand_combination
    return best_comination, max_rank


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    best_comination, _ = count_best_combination_rank(hand)
    return best_comination


def transform_wild_to_simple(hands):
    """ Трансформируем руку с джокером в множество различных рук
      которые получаются при замене джокера на обычную карту """
    new_hands = []
    for hand in hands:
        found_jokers = 0
        for i in range(0, len(hand)):
            card = hand[i]
            if card[Card.RANK_INDEX_IN_CARD] == JokerIterator.JOKER_SYMBOL:
                joker_iterator = JokerIterator(card)
                for new_card in joker_iterator:
                    if new_card not in hand:
                        new_hand = list(hand)
                        new_hand[i] = new_card
                        new_hands.append(new_hand)
                found_jokers += 1
                break
        if found_jokers > 0:
            new_hands = transform_wild_to_simple(new_hands)
        else:
            return hands
    return new_hands


def best_wild_hand(hand):
    hands = transform_wild_to_simple([hand])
    best_comination = []
    max_rank = 0
    for hand in hands:
        # print(hand)
        curr_combination, curr_rank = count_best_combination_rank(hand)
        # print(curr_combination)
        if curr_rank > max_rank:
            max_rank = curr_rank
            best_comination = curr_combination
    return best_comination


def test_best_hand():
    print "test_best_hand..."
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


def test_best_wild_hand():
    print "test_best_wild_hand..."
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print 'OK'


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
