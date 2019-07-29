import itertools
from abc import ABC
from typing import Sequence, Dict, List
from enum import Enum
from random import randint


# ♠ ♤ ♥ ♡ ♣ ♧ ♦ ♢


class CardValue:

    def __init__(self, values: Sequence[int]):
        self.values = values


class CardColor(Enum):
    SPADES = "♤"
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♧"

    def __lt__(self, other):
        """
        Stupid not need method for rubbish python groupby which needs sorting.
        """
        return self.name < other.name

    # ALL_COLORS = [SPADES, HEART, DIAMOND, CLUB]


class CardType(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    def __lt__(self, other):
        """
        Stupid not need method for rubbish python groupby which needs sorting.
        """
        return self.name < other.name

    # def __init__(self, name: str):
    #     self.name = name
    #
    # def __eq__(self, other):
    #     return self.name == other.name
    #
    # def __hash__(self):
    #     return hash(self.name)


card_values: Dict[CardType, Sequence[int]] = {
    CardType.ACE: [11, 1],
    CardType.TWO: [2],
    CardType.THREE: [3],
    CardType.FOUR: [4],
    CardType.FIVE: [5],
    CardType.SIX: [6],
    CardType.SEVEN: [7],
    CardType.EIGHT: [8],
    CardType.NINE: [9],
    CardType.TEN: [10],
    CardType.JACK: [10],
    CardType.QUEEN: [10],
    CardType.KING: [10],
}


class Card:
    card_color: CardColor
    card_type: CardType

    def __init__(self, card_type: CardType, card_color: CardColor):
        self.card_type = card_type
        self.card_color = card_color

    def __str__(self):
        return f"{self.card_type.value}{self.card_color.value}"

    def __repr__(self):
        return self.__str__()
    
    def __key(self):
        return self.card_type, self.card_color

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())


class Deck:

    cards: Sequence[Card]

    def __init__(self):
        self.cards = list(map(lambda card: Card(card[0], card[1]), itertools.product(CardType, CardColor)))

    def get_card(self, index: int) -> Card:
        card = self.cards[index]
        del self.cards[index]
        return card


class Shuffle:

    def next_card_index(self, deck: Deck) -> int:
        raise NotImplementedError()


class RandomShuffle(Shuffle, ABC):

    def next_card_index(self, deck: Deck) -> int:
        cards_left: int = len(deck.cards)
        return randint(0, cards_left - 1)


class Croupier:

    shuffle: Shuffle
    deck: Deck

    def __init__(self, deck: Deck, shuffle: Shuffle):
        self.shuffle = shuffle
        self.deck = deck

    def get_cards_left_in_deck(self) -> Sequence[Card]:
        return self.deck.cards

    def next_card(self) -> Card:
        next_card_index = self.shuffle.next_card_index(self.deck)
        return self.deck.get_card(next_card_index)

    def next_few_cards(self, cards_number: int) -> List[Card]:
        return list(map(lambda _: self.next_card(), ([1]*cards_number)))

class PlayerResultKeeper:
    MAX_SCORE: int = 21

    player_cards: List[Card]

    def busts(self, cards: List[Card]) -> bool:
        return self.cards_value(cards) > self.MAX_SCORE


class GameResultKeeper:

    MAX_SCORE: int = 21

    human_player_cards: List[Card]
    croupier_cards: List[Card]

    def __init__(self):
        self.human_player_cards = []
        self.croupier_cards = []

    def start(self, human_player_cards: List[Card], croupier_cards: List[Card]):
        self.player_hit(human_player_cards)
        self.croupier_hit(croupier_cards)

    def get_croupier_cards(self) -> Sequence[Card]:
        return self.croupier_cards

    def get_human_player_cards(self) -> Sequence[Card]:
        return self.human_player_cards

    def croupier_hit(self, cards: List[Card]):
        self.croupier_cards.extend(cards)

    def player_hit(self, cards: List[Card]):
        self.human_player_cards.extend(cards)

    def deuce(self) -> bool:
        return False

    def croupier_wins(self) -> bool:
        return (not self.croupier_busts()) and (self.player_busts()
            or self.first_hand_values_higher_then_second(self.croupier_cards, self.human_player_cards))

    def player_wins(self) -> bool:
        return (not self.player_busts()) and (self.croupier_busts()
            or self.first_hand_values_higher_then_second(self.human_player_cards, self.croupier_cards))

    def croupier_busts(self) -> bool:
        return self.busts(self.croupier_cards)

    def player_busts(self) -> bool:
        return self.busts(self.human_player_cards)

    def cards_value(self, cards: List[Card]) -> int:
        return sum(map(lambda card: card_values[card.card_type][0], cards))

    def busts(self, cards: List[Card]) -> bool:
        return self.cards_value(cards) > self.MAX_SCORE

    def first_hand_values_higher_then_second(self, hand1: List[Card], hand2: List[Card]):
        return self.cards_value(hand1) > self.cards_value(hand2)


class Game:

    croupier: Croupier
    result_keeper: GameResultKeeper

    was_croupier_hit: bool = False

    def __init__(self, croupier: Croupier, result_keeper: GameResultKeeper):
        self.croupier = croupier
        self.result_keeper = result_keeper

    def __getattr__(self, attr):
        return getattr(self.result_keeper, attr)

    def start(self) -> None:
        self.result_keeper.start(self.croupier.next_few_cards(2), self.croupier.next_few_cards(2))

    def get_cards_left_in_deck(self) -> Sequence[Card]:
        return self.croupier.get_cards_left_in_deck()

    def croupier_hit(self):
        self.result_keeper.croupier_hit(self.croupier.next_few_cards(1))

    def player_hit(self):
        self.result_keeper.player_hit(self.croupier.next_few_cards(1))


class GameFactory:

    def croupier(self, shuffle: Shuffle):
        return Croupier(Deck(), shuffle)

    def game_with_shuffle(self, shuffle: Shuffle):
        return Game(self.croupier(shuffle), GameResultKeeper())

    def game(self) -> Game:
        RandomShuffle()
        return self.game_with_shuffle(RandomShuffle())


if __name__ == "__main__":
    print(list(map(lambda card: Card(card[0], card[1]), itertools.product(CardType, CardColor))))
    print("♠ ♤ ♥ ♡ ♣ ♧ ♦ ♢")
    print(list(CardColor))
    print(CardColor.CLUB.name)
    print(CardColor.CLUB.value)
