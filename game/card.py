import random


class Card():
    def __init__(self, sttn, is_red):
        self.sttn = sttn
        self.is_red = is_red
        self.is_mid = False

    def set_is_mid(self):
        self.is_mid = True

    @property
    def info(self):
        return {
            "sttn": self.sttn,
            "is_red": self.is_red,
            "is_mid": self.is_mid
        }


class Cards():
    def __init__(self, order=None):
        if order == None:
            self.order = [_ for _ in range(11)]
            random.shuffle(self.order)

        self.cards = {}
        idx = 1
        for is_red in [True, False]:
            for sttn in range(1, 6):
                self.cards[idx] = Card(sttn, is_red)
                idx += 1

        self.end_num = 0

    def set_order(self, order):
        self.order = order

    def draw(self):
        idx = self.order.pop()
        if idx == 0:
            idx = self.order.pop()
            self.cards[idx].set_is_mid()
        self.end_num += int(self.cards[idx].is_red)
        return self.cards[idx]


if __name__ == "__main__":
    tmp = Cards()
    print(tmp.order)
    while tmp.end_num < 5:
        card = tmp.draw()
        print(card.info)
