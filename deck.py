import random

# from constant import *

SUITS = ['C', 'S', 'H', 'D']
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']


class Deck:
    def __init__(self):
        self.hands = None
        # self.users = {}
        self.cards = []
        self.build()

    def build(self):
        for rank in RANKS:
            for suit in SUITS:
                self.cards.append(rank + suit)

    def shuffle(self):
        random.shuffle(self.cards)
        return self.cards

    def deal(self, number_of_players):
        self.hands = [self.cards[i::number_of_players] for i in range(0, number_of_players)]
        return self.hands
        # if len(self.cards) > 1:
        #     return str(self.cards.pop())

    # def getCards(self):
    #     while len(self.cards) > 0:
    #         for i in range(0, self.number_of_players):
    #             self.users[i] = self.deal()
