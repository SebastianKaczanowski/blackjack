# from __future__ import annotations (works in 3.7 +)
import unittest
from abc import ABC

from typing import Sequence, List
from itertools import groupby
from blackjack import Game, Card, GameFactory, CardType, CardColor, Shuffle, Deck


class GivenOrderShuffle(Shuffle, ABC):
    cards: List[Card]

    def __init__(self, cards: List[Card]):
        self.cards = cards
        self.cards.reverse()

    def next_card_index(self, deck: Deck) -> int:
        next_card: Card = self.cards.pop()
        return deck.cards.index(next_card)


# ♤ ♥ ♧ ♦

def str_to_card(s: str, index: int = 0) -> Card:
    return Card(CardType(s[index]), CardColor(s[index + 1]))


def c(s: str) -> Card:
    return str_to_card(s)


def cs(s: str, separator_len: int = 1) -> List[Card]:
    return list(map(lambda index: str_to_card(s, index), range(0, len(s), 2 + separator_len)))


class GameResult:
    deuce: bool = False

    player_busts: bool = False

    croupier_busts: bool = False

    croupier_wins: bool = False

    player_wins: bool = False

    def make_player_winning(self):
        self.player_wins = True
        return self

    def make_croupier_winning(self):
        self.croupier_wins = True
        return self

    def make_croupier_bust(self):
        self.croupier_busts = True
        return self.make_player_winning()

    def assert_game_result(self, game: Game, test_case: unittest.TestCase) -> None:
        test_case.assertEqual(self.deuce, game.deuce())
        test_case.assertEqual(self.player_busts, game.player_busts())
        test_case.assertEqual(self.croupier_busts, game.croupier_busts())
        test_case.assertEqual(self.croupier_wins, game.croupier_wins())
        test_case.assertEqual(self.player_wins, game.player_wins())

    @staticmethod
    def players_win_check(game: Game, test_case: unittest.TestCase) -> None:
        result = GameResult()
        result.make_player_winning()
        result.assert_game_result(game, test_case)

    @staticmethod
    def croupier_win_check(game: Game, test_case: unittest.TestCase) -> None:
        result = GameResult()
        result.make_croupier_winning()
        result.assert_game_result(game, test_case)


class BlackjackTest(unittest.TestCase):
    factory: GameFactory = GameFactory()

    def test_1(self):
        print(cs("A♤ Q♥ 2♦"))

    def test_win(self):
        croupier_cards: str = "2♦ 4♧ 5♤ J♧"

        game = self.factory.game_with_shuffle(GivenOrderShuffle(
            cs("K♤ Q♥ " + croupier_cards)
        ))
        game.start()
        GameResult.players_win_check(game, self)

        game.croupier_hit()
        game.croupier_hit()
        GameResult.croupier_win_check(game, self)

        self.assertEqual(cs(croupier_cards), game.croupier_cards)

    def check_one_hand(self, hand: str, expectedResult: GameResult):
        cards = cs(hand, 2)
        game = self.factory.game_with_shuffle(GivenOrderShuffle(cards))
        game.start()
        actions = list(map(lambda index: hand[index], range(2, len(hand), 4)))

        for action in actions[4:]:
            if action == "p":
                game.player_hit()
            else:
                game.croupier_hit()

        expectedResult.assert_game_result(game, self)

    def test_various_hands(self):
        self.check_one_hand("K♤p Q♥p 2♦c 4♧c 5♤c J♧c", GameResult().make_croupier_winning())
        self.check_one_hand("K♤p Q♥p 3♦c 4♧c 5♤c J♧c", GameResult().make_croupier_bust())

    def test_card_equal(self):
        print(Card(CardType.KING, CardColor.CLUB))
        print({Card(CardType.KING, CardColor.CLUB), Card(CardType.QUEEN, CardColor.DIAMOND)})

    def test_should_start_game_each_time_in_a_different_way(self):
        game1_start = self.game_properly_started(self.factory.game())
        game2_start = self.game_properly_started(self.factory.game())
        self.assertNotEqual(game1_start, game2_start)

    def test_should_start_game_correctly(self):
        game = self.factory.game()
        self.game_properly_started(game)

    #
    # helpers
    #

    def game_properly_started(self, game) -> (Sequence[Card], Sequence[Card], Sequence[Card]):
        game.start()
        human_player_cards = game.get_human_player_cards()
        croupier_cards = game.get_croupier_cards()
        left_in_deck = game.get_cards_left_in_deck()
        self.check_cards_number(human_player_cards)
        self.check_cards_number(croupier_cards)
        self.check_cards_number(left_in_deck, 52 - 4)
        self.check_cards_in_game(game)
        return human_player_cards, croupier_cards, left_in_deck

    def check_cards_in_game(self, game: Game):
        all_cards = self.get_all_cards_from_game(game)
        by_colors = self.group_cards_by_colors(all_cards)
        self.all_cards_are_present(by_colors)

    def all_cards_are_present(self, by_colors):
        self.assertEqual(set(CardColor), set(map(lambda p: p[0], by_colors)))
        all_card_types = set(CardType)
        for _, cards in by_colors:
            card_type = set(map(lambda card: card.card_type, list(cards)))
            self.assertEqual(all_card_types, card_type)

    def group_cards_by_colors(self, all_cards):
        tmp = sorted(all_cards, key=lambda c: c.card_color)
        by_colors = [(c, list(cgen)) for c, cgen in groupby(tmp, key=lambda c: c.card_color)]
        return by_colors

    def get_all_cards_from_game(self, game):
        all_cards = set(game.get_human_player_cards())
        all_cards.update(game.get_croupier_cards())
        all_cards.update(game.get_cards_left_in_deck())
        self.check_cards_number(all_cards, 52)
        return all_cards

    def check_cards_number(self, human_cards, expected_cards_number=2):
        self.check_size(expected_cards_number, human_cards)
        self.cards_only(human_cards)

    def check_size(self, expected_cards_number, human_cards):
        self.assertEqual(expected_cards_number, len(human_cards))

    def cards_only(self, cards):
        for card in cards:
            self.assertIsInstance(card, Card)


if __name__ == "__main__":
    unittest.main(verbosity=2)
