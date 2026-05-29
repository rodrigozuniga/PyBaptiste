class Card:
    SUITS = ("Clubs", "Diamonds", "Hearts", "Spades")
    RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")

    def __init__(self, rank, suit):
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Deck({len(self)} cards)"

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def deal(self, num=1):
        if num > len(self.cards):
            raise ValueError(f"Not enough cards: requested {num}, have {len(self.cards)}")
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt if num > 1 else dealt[0]


if __name__ == "__main__":
    deck = Deck()
    print(f"Created: {deck}")
    print(f"First 5 cards: {deck.cards[:5]}")
    deck.shuffle()
    print(f"After shuffle, first 5: {deck.cards[:5]}")
    hand = deck.deal(5)
    print(f"Dealt hand: {hand}")
    print(f"Remaining: {deck}")
