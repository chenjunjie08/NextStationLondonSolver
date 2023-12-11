from node import Node
from connect import Connect
from card import Cards
from config import Config


class Game():
    # Init the map, mainly some fixed setting.
    def __init__(self):
        self.nodes = {}
        self.connects = []

        # node generate
        node_pos = []
        with open('./game/node_pos.txt') as f:
            for line in f.readlines():
                node_pos.append(line.strip())
        self.map_h = len(node_pos)
        self.map_w = len(node_pos[0])

        # line, column, sttn, dist
        idx = 0
        self.nodes_position = {}
        for idx_line, line in enumerate(node_pos):
            for idx_column, node in enumerate(line):
                if node != '0':
                    self.nodes[idx] = Node(idx)
                    self.nodes[idx].set_pos(idx_line, idx_column)
                    self.nodes[idx].set_sttn(int(node))
                    self.nodes_position[(idx_line, idx_column)] = idx

                    if idx_line <= 2:
                        if idx_column == 0 and idx_line == 0:
                            self.nodes[idx].set_dst(0)
                        elif idx_column <= 2:
                            self.nodes[idx].set_dst(1)
                        elif idx_column <= 6:
                            self.nodes[idx].set_dst(2)
                        elif idx_column == 9 and idx_line == 0:
                            self.nodes[idx].set_dst(4)
                        else:
                            self.nodes[idx].set_dst(3)
                    elif idx_line <= 6:
                        if idx_column <= 2:
                            self.nodes[idx].set_dst(5)
                        elif idx_column <= 6:
                            self.nodes[idx].set_dst(6)
                        else:
                            self.nodes[idx].set_dst(7)
                    else:
                        if idx_column == 0 and idx_line == 9:
                            self.nodes[idx].set_dst(8)
                        elif idx_column <= 2:
                            self.nodes[idx].set_dst(9)
                        elif idx_column <= 6:
                            self.nodes[idx].set_dst(10)
                        elif idx_column == 9 and idx_line == 9:
                            self.nodes[idx].set_dst(12)
                        else:
                            self.nodes[idx].set_dst(11)

                    idx += 1

        # adjacent, connect
        directions = [(-1, 1), (0, 1), (1, 1), (1, 0)]
        for idx in range(len(self.nodes)):
            begin_pos = self.nodes[idx].pos
            for direction in directions:
                current_pos = begin_pos.copy()
                while 0 <= current_pos[0] < self.map_h and 0 <= current_pos[1] < self.map_w:
                    tar_idx = self.nodes_position.get(tuple(current_pos))
                    if tar_idx is not None and tar_idx != idx:
                        self.nodes[idx].set_adj(self.nodes[tar_idx])
                        self.connects.append(
                            Connect(self.nodes[idx], self.nodes[tar_idx])
                        )
                        current_pos = [-1, -1]
                        continue
                    else:
                        current_pos[0] += direction[0]
                        current_pos[1] += direction[1]

        # cross river?
        river = [
            [[3.50, -0.1], [3.50, 2.10]],
            [[3.40, 1.90], [5.26, 3.76]],
            [[5.25, 3.74], [5.25, 5.10]],
            [[5.26, 4.99], [4.40, 6.10]],
            [[4.50, 5.90], [4.50, 9.10]],
        ]
        for connect in self.connects:
            for pos1, pos2 in river:
                if connect.is_intersect(pos1=pos1, pos2=pos2):
                    connect.set_cross_river()
                    break

        # is tourist
        for idx in [9, 16, 19, 36, 49]:
            self.nodes[idx].set_is_trt()

        # color
        self.nodes[13].set_color(0)
        self.nodes[29].set_color(1)
        self.nodes[21].set_color(2)
        self.nodes[40].set_color(3)
        self.nodes_head = [13, 29, 21, 40]

        # TODO: goals

        # TODO: pencil ability

        # game config
        self.config = Config()

    @staticmethod
    def connect_search(connnect_list, idx1, idx2):
        for idx, connect in enumerate(connnect_list):
            if connect.endpoint[0].id == min(idx1, idx2) and connect.endpoint[1].id == max(idx1, idx2):
                return idx
        return -1

    def game_config(self, config):
        self.config = Config(config)

    def new_game(self, mode='step'):
        assert mode in ['random', 'fix', 'step']

        # init game, but store config
        config_tmp = self.config
        self.__init__()
        self.config = config_tmp

        # init score
        self.total_score = 0
        self.round_score = [0, 0, 0, 0]
        self.inter_score = [0, 0, 0]
        self.goals_score = [0, 0]

        # init round
        self.round = 0

        # init color
        self.color = None

        print("Game Start!\n")

        print("### Round 1 ###")

        while self.round <= 3:

            if mode == 'step':
                self.color = int(input(f'color of round {self.round+1} is: '))
            # init heads, nodes, and connects
            heads = [self.nodes_head[self.color]]
            nodes = [self.nodes_head[self.color]]
            connects = []

            # init new cards
            cards = Cards()

            while cards.end_num <= 5:
                card_used = []
                if mode == 'step':
                    card_idx = int(input('Flipped card is: '))
                    card_used.append(card_idx)
                    if card_idx == 0:
                        card_idx = input('Next card is: ')
                        card_used.append(card_idx)
                        cards.cards[card_idx].set_is_mid()
                    card = cards.cards[card_idx]
                    cards.end_num += int(card.is_red)

                else:
                    # TODO: random and fix game
                    pass

                # possible move
                if card.is_mid:
                    possible_move = self.possible_move(nodes, card.sttn)
                else:
                    possible_move = self.possible_move(heads, card.sttn)

                # take action
                while True:
                    action = input("Your action: ")
                    if action == 'show':
                        self.show(card, card_used, possible_move)
                        continue
                    if action == 'pass':
                        continue

    def possible_move(self, heads, sttn):
        move = {}
        for idx, connect in enumerate(self.connects):
            if not connect.is_available:
                continue
            if not (connect.endpoint[0].id in heads or connect.endpoint[1].id in heads):
                continue

            if connect.endpoint[0].id in heads:
                begin = connect.endpoint[0].id
                end = connect.endpoint[1]
            else:
                begin = connect.endpoint[1].id
                end = connect.endpoint[0]

            if sttn == 5 or end.sttn == sttn:
                if move.get(begin) is None:
                    move[begin] = [end.id]
                else:
                    move[begin].append(end.id)

        return move

    def show(self, card, card_used, move):
        print()
        print("### current info ###")
        print(f"Round: {self.round+1}")
        print(f"color: {self.color}")
        print(
            f"current card: {card.sttn}, {'red' if card.is_red else 'blue'}, {'mid' if card.is_mid else 'head'}")
        print(f"possible move: {'pass' if len(move)==0 else ''}")
        if len(move) > 0:
            for key, values in move.items():
                print(f"{key} to {','.join([str(value) for value in values])}")
        print(f"used card: {card_used[:-1]}")
        print(f"score: {self.total_score}")

        print()


if __name__ == "__main__":
    tmp = Game()
    tmp.new_game()
    # print(tmp.nodes[40].info)
    # print(tmp.connects[69].info)
    # print(tmp.connects[83].info)
    # print(tmp.connect_search(tmp.connects, 26, 35))
    # print(tmp.connects[84].is_intersect(tmp.connects[69]))\
