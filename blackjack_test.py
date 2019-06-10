import unittest

from typing import Sequence
from itertools import groupby
from blackjack import Game, Card, GameFactory, CardType, CardColor


class BlackjackTest(unittest.TestCase):
    factory: GameFactory = GameFactory()

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
