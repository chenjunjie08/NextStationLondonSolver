from node import Node
from connect import Connect
from card import Cards
import numpy as np
import random
import copy
from tqdm import tqdm
import pickle
import pdb


# input an int or retry
def safe_input(prompt):
    while True:
        try:
            res = int(input(prompt))
        except ValueError:
            continue
        return res


class Game():
    # Init the map, mainly some fixed setting.
    def __init__(self):
        self.nodes = {}
        self.connects = []

        # node generate
        node_pos = []
        with open('Game/envs/node_pos.txt') as f:
            for line in f.readlines():
                node_pos.append(line.strip())
        self.map_h = len(node_pos)
        self.map_w = len(node_pos[0])

        # line, column, sttn, dist
        idx = 0
        nodes_position = {}
        for idx_line, line in enumerate(node_pos):
            for idx_column, node in enumerate(line):
                if node != '0':
                    self.nodes[idx] = Node(idx)
                    self.nodes[idx].set_pos(idx_line, idx_column)
                    self.nodes[idx].set_sttn(int(node))
                    nodes_position[(idx_line, idx_column)] = idx

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
                    tar_idx = nodes_position.get(tuple(current_pos))
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
        self.nodes_head = [13, 29, 21, 40]

    @staticmethod
    def connect_search(connnect_list, idx1, idx2):
        for idx, connect in enumerate(connnect_list):
            if connect.endpoint[0].id == min(idx1, idx2) and connect.endpoint[1].id == max(idx1, idx2):
                return idx
        return -1

    def new_game(self, mode='step', active_power=False, auto_play=False, actor=None):
        assert mode in ['random', 'fix', 'step']

        # init game
        self.__init__()

        # init round
        round = -1

        # init color
        if mode == 'random':
            colors = [0, 1, 2, 3]
            random.shuffle(colors)

        # init score
        total_score = 0
        river_score = np.array([0, 0, 0, 0])
        dst_score = np.array([0, 0, 0, 0])
        inter_score = np.array([0, 0, 0])
        trt_score = np.array([0, 1, 2, 4, 6, 8, 11, 14, 17, 21, 25])
        goals_score = np.array([0, 0, 0, 0, 0])
        goals_used = np.array([0, 0, 0, 0, 0])

        # init goal-related var
        dsts_total = np.array([0 for _ in range(13)])
        trts_total = [9, 16, 19, 36, 49]
        cntr_total = [18, 19, 20, 25, 26, 30, 32, 33, 34]

        print("Game Start!\n")
        if mode == 'step':
            goals = input("Goals of this game: ").split(",")
            for goal in goals:
                goals_used[int(goal)] = 1
        elif mode == 'random':
            goals_used[np.random.choice([0, 1, 2, 3, 4], 2, False)] = 1

        while round < 3:
            round += 1
            print(f"### Round {round+1} ###")

            # color used in this round
            if mode == 'step':
                color = safe_input(f'color of round {round+1} is: ')
            elif mode == 'random':
                color = colors[round]

            # init heads, nodes, and connects
            heads = [self.nodes_head[color]]
            nodes = [self.nodes_head[color]]
            connects = []
            self.nodes[self.nodes_head[color]].set_color(color)

            # init new cards
            cards = Cards()
            card_used = []
            if mode == 'random':
                card_orders = [_ for _ in range(11)]
                random.shuffle(card_orders)

            # init dst
            dsts = np.array([0 for _ in range(13)])
            dsts[self.nodes[self.nodes_head[color]].dst] += 1

            # init power
            if active_power:
                power = safe_input('Power is: ')
                power_used = False
            double_count = 0

            while cards.end_num <= 4:
                if mode == 'step':
                    card_idx = safe_input('Flipped card is: ')
                    card_used.append(card_idx)
                    if card_idx == 0:
                        card_idx = safe_input('Next card is: ')
                        card_used.append(card_idx)
                        cards.cards[card_idx].set_is_mid()
                    card = cards.cards[card_idx]
                    cards.end_num += int(card.is_red)

                elif mode == 'random':
                    card_idx = card_orders.pop(0)
                    card_used.append(card_idx)
                    if card_idx == 0:
                        card_idx = card_orders.pop(0)
                        card_used.append(card_idx)
                        cards.cards[card_idx].set_is_mid()
                    card = cards.cards[card_idx]
                    cards.end_num += int(card.is_red)

                # possible move
                if card.is_mid:
                    possible_move = self.possible_move(nodes, nodes, card.sttn)
                else:
                    possible_move = self.possible_move(heads, nodes, card.sttn)

                # take action
                while True:
                    if auto_play:
                        if actor is None:
                            action = self.random_act(possible_move)
                        else:
                            situation = {
                                'goals_used': goals_used,

                                'round': round,
                                'color': color,

                                'active_power': active_power,
                                'power': power,
                                'power_used': power_used,
                                'double_count': double_count,

                                'heads': heads,
                                'nodes': nodes,
                                'connects': connects,
                                'dsts': dsts,

                                'card_used': card_used,
                                'card': card,
                                'card_idx': card_idx,
                                'possible_move': possible_move,

                                'total_score': total_score,
                                'river_score': river_score,
                                'dst_score': dst_score,
                                'inter_score': inter_score,
                                'trt_score': trt_score,
                                'goals_score': goals_score,

                                'dsts_total': dsts_total,
                                'trts_total': trts_total,
                                'cntr_total': cntr_total,
                            }
                            action = actor(copy.deepcopy(self),
                                           copy.deepcopy(situation))
                        print(
                            f"AI: Card is {'0-' if card.is_mid else ''}{card_idx}. I choose {action}. "
                        )
                    else:
                        action = input("Your action: ")

                    if action in ['show', 's']:
                        self.show(round, color, card, card_used,
                                  possible_move, nodes, connects, total_score)
                        continue
                    if action in ['pass', 'p']:
                        break

                    if action == 'power':
                        if power_used:
                            print("Power Already Used!\n")
                            continue

                        if power == 0:
                            double_count = 1
                        elif power == 1:
                            card.sttn = 5
                        elif power == 2:
                            card.set_is_mid()
                        elif power == 3:
                            # simplified action, will only put x2 at the most crowded dst
                            dsts_most = np.random.choice(
                                np.where(dsts == dsts.max())[0])
                            dsts[dsts_most] += 1
                            print(f"Dist {dsts_most} has a x2 mark")
                        else:
                            print("Invalid power!\n")
                            continue

                        power_used = True
                        # possible move
                        if card.is_mid:
                            possible_move = self.possible_move(
                                nodes, nodes, card.sttn)
                        else:
                            possible_move = self.possible_move(
                                heads, nodes, card.sttn)
                        continue

                    try:
                        begin, end = action.split('-')
                        begin = int(begin)
                        end = int(end)
                    except:
                        print("input: show, pass, or xx-xx\n")
                        continue

                    # check if valid
                    if begin in possible_move.keys() and end in possible_move[begin]:
                        pass
                    else:
                        print("Move invalid!\n")
                        continue

                    # modify heads
                    if len(heads) == 1:
                        heads.append(end)
                    elif not begin in heads:
                        heads.append(end)
                    else:
                        for idx, head in enumerate(heads):
                            if head == begin:
                                heads[idx] = end
                                break

                    # modify nodes
                    nodes.append(end)

                    dsts[self.nodes[end].dst] += 1
                    dst_score[round] = self.score_dst(dsts)
                    # goal 1
                    if goals_score[1] == 0:
                        dsts_total[self.nodes[end].dst] = 1
                        if dsts_total.sum() == 13:
                            goals_score[1] == 1

                    if self.nodes[end].is_trt:
                        if len(trt_score) > 1:
                            trt_score = trt_score[1:]
                        # goal 2
                        if goals_score[2] == 0:
                            for idx, val in enumerate(trts_total):
                                if self.nodes[end].id == val:
                                    trts_total.pop(idx)
                                    break
                            if len(trts_total) == 0:
                                goals_score[2] = 1

                    # goal 3
                    if goals_score[3] == 0:
                        for idx, val in enumerate(cntr_total):
                            if self.nodes[end].id == val:
                                cntr_total.pop(idx)
                                break
                        if len(cntr_total) == 0:
                            goals_score[3] = 1

                    self.nodes[end].set_color(color)
                    if sum(self.nodes[end].color) < 2:
                        pass
                    elif sum(self.nodes[end].color) == 2:
                        inter_score[0] += 1
                    elif sum(self.nodes[end].color) == 3:
                        inter_score[0] -= 1
                        inter_score[1] += 1
                    elif sum(self.nodes[end].color) == 4:
                        inter_score[1] -= 1
                        inter_score[2] += 1

                    if len(nodes) == 2:
                        if sum(self.nodes[begin].color) < 2:
                            pass
                        elif sum(self.nodes[begin].color) == 2:
                            inter_score[0] += 1
                        elif sum(self.nodes[begin].color) == 3:
                            inter_score[0] -= 1
                            inter_score[1] += 1
                        elif sum(self.nodes[begin].color) == 4:
                            inter_score[1] -= 1
                            inter_score[2] += 1

                    # goal 0
                    if goals_score[0] == 0 and inter_score.sum() >= 8:
                        goals_score[0] = 1

                    # modify connects
                    connect_id = self.connect_search(self.connects, begin, end)
                    connects.append(connect_id)
                    if self.connects[connect_id].is_cross_river:
                        river_score[round] += 1
                    # goal 4
                    if goals_score[4] == 0 and river_score.sum() >= 6:
                        goals_score[4] = 1

                    self.connects[connect_id].set_unavailable()
                    for idx in range(len(self.connects)):
                        if idx == connect_id:
                            continue
                        if not self.connects[idx].is_available:
                            continue
                        if self.connects[connect_id].is_intersect(self.connects[idx]):
                            self.connects[idx].set_unavailable()

                    total_score = self.score_total(
                        river_score, dst_score, trt_score, inter_score, goals_score, goals_used)
                    # print(f"Current score is {total_score}\n")

                    # power: double
                    if double_count == 0:
                        pass
                    elif double_count == 1:
                        double_count = 2
                        if card.sttn == 5:
                            card.sttn = self.nodes[end].sttn
                        # possible move
                        if card.is_mid:
                            possible_move = self.possible_move(
                                nodes, nodes, card.sttn)
                        else:
                            possible_move = self.possible_move(
                                heads, nodes, card.sttn)
                        continue
                    elif double_count == 2:
                        double_count = 0

                    break

        # Game over
        print(f"\nGame end!")
        print(f"Score: {total_score}")
        print(
            f"Goals finished: {', '.join(np.where(goals_score > 0)[0].astype(str))}")

        return total_score

    # for generating data and quick test
    def new_game_quiet(self, active_power=False, actor=None, is_save=False):
        # whether save data
        if is_save:
            save_data = []

        # init game
        self.__init__()

        # init round
        round = -1

        # init color
        colors = [0, 1, 2, 3]
        random.shuffle(colors)

        # init score
        total_score = 0
        river_score = np.array([0, 0, 0, 0])
        dst_score = np.array([0, 0, 0, 0])
        inter_score = np.array([0, 0, 0])
        trt_score = np.array([0, 1, 2, 4, 6, 8, 11, 14, 17, 21, 25])
        goals_score = np.array([0, 0, 0, 0, 0])
        goals_used = np.array([0, 0, 0, 0, 0])
        goals_used[np.random.choice([0, 1, 2, 3, 4], 2, False)] = 1

        # init goal-related var
        dsts_total = np.array([0 for _ in range(13)])
        trts_total = [9, 16, 19, 36, 49]
        cntr_total = [18, 19, 20, 25, 26, 30, 32, 33, 34]

        while round < 3:
            round += 1

            # color used in this round
            color = colors[round]

            # init heads, nodes, and connects
            heads = [self.nodes_head[color]]
            nodes = [self.nodes_head[color]]
            connects = []
            self.nodes[self.nodes_head[color]].set_color(color)

            # init new cards
            cards = Cards()
            card_used = []
            card_orders = [_ for _ in range(11)]
            random.shuffle(card_orders)

            # init dst
            dsts = np.array([0 for _ in range(13)])
            dsts[self.nodes[self.nodes_head[color]].dst] += 1

            # init power
            if active_power:
                power = safe_input('Power is: ')
                power_used = False
            double_count = 0

            while cards.end_num <= 4:
                card_idx = card_orders.pop(0)
                card_used.append(card_idx)
                if card_idx == 0:
                    card_idx = card_orders.pop(0)
                    card_used.append(card_idx)
                    cards.cards[card_idx].set_is_mid()
                card = cards.cards[card_idx]
                cards.end_num += int(card.is_red)

                # possible move
                if card.is_mid:
                    possible_move = self.possible_move(nodes, nodes, card.sttn)
                else:
                    possible_move = self.possible_move(heads, nodes, card.sttn)

                # take action
                while True:
                    situation = {
                        'goals_used': goals_used,

                        'round': round,
                        'color': color,

                        'active_power': active_power,
                        'power': power,
                        'power_used': power_used,
                        'double_count': double_count,

                        'heads': heads,
                        'nodes': nodes,
                        'connects': connects,
                        'dsts': dsts,

                        'card_used': card_used,
                        'card': card,
                        'card_idx': card_idx,
                        'possible_move': possible_move,

                        'total_score': total_score,
                        'river_score': river_score,
                        'dst_score': dst_score,
                        'inter_score': inter_score,
                        'trt_score': trt_score,
                        'goals_score': goals_score,

                        'dsts_total': dsts_total,
                        'trts_total': trts_total,
                        'cntr_total': cntr_total,
                    }
                    if is_save:
                        save_data.append(self.save_data(
                            copy.deepcopy(situation)))
                    if actor is None:
                        action = self.random_act(possible_move)
                    else:
                        action = actor(copy.deepcopy(self),
                                       copy.deepcopy(situation))

                    # if action in ['show', 's']:
                    #     self.show(round, color, card, card_used,
                    #               possible_move, nodes, connects, total_score)
                    #     continue
                    if action in ['pass', 'p']:
                        break

                    if action == 'power':
                        if power_used:
                            print("Power Already Used!\n")
                            continue

                        if power == 0:
                            double_count = 1
                        elif power == 1:
                            card.sttn = 5
                        elif power == 2:
                            card.set_is_mid()
                        elif power == 3:
                            # simplified action, will only put x2 at the most crowded dst
                            dsts_most = np.random.choice(
                                np.where(dsts == dsts.max())[0])
                            dsts[dsts_most] += 1
                            print(f"Dist {dsts_most} has a x2 mark")
                        else:
                            print("Invalid power!\n")
                            continue

                        power_used = True
                        # possible move
                        if card.is_mid:
                            possible_move = self.possible_move(
                                nodes, nodes, card.sttn)
                        else:
                            possible_move = self.possible_move(
                                heads, nodes, card.sttn)
                        continue

                    try:
                        begin, end = action.split('-')
                        begin = int(begin)
                        end = int(end)
                    except:
                        print("input: show, pass, or xx-xx\n")
                        continue

                    # check if valid
                    if begin in possible_move.keys() and end in possible_move[begin]:
                        pass
                    else:
                        print("Move invalid!\n")
                        continue

                    # modify heads
                    if len(heads) == 1:
                        heads.append(end)
                    elif not begin in heads:
                        heads.append(end)
                    else:
                        for idx, head in enumerate(heads):
                            if head == begin:
                                heads[idx] = end
                                break

                    # modify nodes
                    nodes.append(end)

                    dsts[self.nodes[end].dst] += 1
                    dst_score[round] = self.score_dst(dsts)
                    # goal 1
                    if goals_score[1] == 0:
                        dsts_total[self.nodes[end].dst] = 1
                        if dsts_total.sum() == 13:
                            goals_score[1] == 1

                    if self.nodes[end].is_trt:
                        if len(trt_score) > 1:
                            trt_score = trt_score[1:]
                        # goal 2
                        if goals_score[2] == 0:
                            for idx, val in enumerate(trts_total):
                                if self.nodes[end].id == val:
                                    trts_total.pop(idx)
                                    break
                            if len(trts_total) == 0:
                                goals_score[2] = 1

                    # goal 3
                    if goals_score[3] == 0:
                        for idx, val in enumerate(cntr_total):
                            if self.nodes[end].id == val:
                                cntr_total.pop(idx)
                                break
                        if len(cntr_total) == 0:
                            goals_score[3] = 1

                    self.nodes[end].set_color(color)
                    if sum(self.nodes[end].color) < 2:
                        pass
                    elif sum(self.nodes[end].color) == 2:
                        inter_score[0] += 1
                    elif sum(self.nodes[end].color) == 3:
                        inter_score[0] -= 1
                        inter_score[1] += 1
                    elif sum(self.nodes[end].color) == 4:
                        inter_score[1] -= 1
                        inter_score[2] += 1

                    if len(nodes) == 2:
                        if sum(self.nodes[begin].color) < 2:
                            pass
                        elif sum(self.nodes[begin].color) == 2:
                            inter_score[0] += 1
                        elif sum(self.nodes[begin].color) == 3:
                            inter_score[0] -= 1
                            inter_score[1] += 1
                        elif sum(self.nodes[begin].color) == 4:
                            inter_score[1] -= 1
                            inter_score[2] += 1

                    # goal 0
                    if goals_score[0] == 0 and inter_score.sum() >= 8:
                        goals_score[0] = 1

                    # modify connects
                    connect_id = self.connect_search(self.connects, begin, end)
                    connects.append(connect_id)
                    self.connects[connect_id].set_color(color)
                    if self.connects[connect_id].is_cross_river:
                        river_score[round] += 1
                    # goal 4
                    if goals_score[4] == 0 and river_score.sum() >= 6:
                        goals_score[4] = 1

                    self.connects[connect_id].set_unavailable()
                    for idx in range(len(self.connects)):
                        if idx == connect_id:
                            continue
                        if not self.connects[idx].is_available:
                            continue
                        if self.connects[connect_id].is_intersect(self.connects[idx]):
                            self.connects[idx].set_unavailable()

                    total_score = self.score_total(
                        river_score, dst_score, trt_score, inter_score, goals_score, goals_used)

                    # power: double
                    if double_count == 0:
                        pass
                    elif double_count == 1:
                        double_count = 2
                        if card.sttn == 5:
                            card.sttn = self.nodes[end].sttn
                        # possible move
                        if card.is_mid:
                            possible_move = self.possible_move(
                                nodes, nodes, card.sttn)
                        else:
                            possible_move = self.possible_move(
                                heads, nodes, card.sttn)
                        continue
                    elif double_count == 2:
                        double_count = 0

                    break

        # Game over
        if is_save:
            for idx in range(len(save_data)):
                save_data[idx]['final_score'] = total_score
            return total_score, save_data

        return total_score

    def possible_move(self, heads, nodes, sttn):
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

            # no circle
            if end.id in nodes:
                continue

            if sttn == 5 or end.sttn == sttn or end.sttn == 5:
                if move.get(begin) is None:
                    move[begin] = [end.id]
                else:
                    move[begin].append(end.id)

        return move

    @staticmethod
    def score_total(river_score, dst_score, trt_score, inter_score, goals_score, goals_used):
        total_score = 0
        total_score += river_score.sum() * 2
        total_score += dst_score.sum()
        total_score += trt_score[0]
        total_score += (inter_score * np.array([2, 5, 9])).sum()
        total_score += (goals_score * goals_used).sum() * 10
        return total_score

    @staticmethod
    def random_act(possible_move):
        if len(possible_move) == 0:
            return 'pass'
        begin = random.choice(list(possible_move.keys()))
        end = random.choice(possible_move[begin])
        return f"{begin}-{end}"

    @staticmethod
    def score_dst(dsts):
        return dsts.max() * (dsts > 0).astype(int).sum()

    def save_data(self, situation):
        data = {}

        # nodes info: colors
        nodes_info = []
        for idx in range(len(self.nodes)):
            nodes_info.append(self.nodes[idx].color[:])
        data['nodes_info'] = nodes_info

        # connects info: colors, is_available
        connects_color = []
        connects_avail = []
        for idx in range(len(self.connects)):
            connects_color.append(self.connects[idx].color)
            connects_avail.append(self.connects[idx].is_available)
        data['connects_info'] = (connects_color, connects_avail)

        # situation
        data['situation'] = situation

        return data

    def show(self, round, color, card, card_used, move, nodes, connects, score):
        print()
        print("### current info ###")
        print(f"Round: {round+1}")
        print(f"color: {color}")
        print(
            f"current card: {card.sttn}, {'red' if card.is_red else 'blue'}, {'mid' if card.is_mid else 'head'}")
        print(f"nodes: {','.join([str(node) for node in nodes])}")
        print(
            f"connects: {','.join(['-'.join([str(self.connects[ct].endpoint[0].id), str(self.connects[ct].endpoint[1].id)]) for ct in connects])}")
        print(f"possible move: {'pass' if len(move)==0 else ''}")
        if len(move) > 0:
            for key, values in move.items():
                print(
                    f"- {key} to {','.join([str(value) for value in values])}")
        print(f"used cards: {','.join([str(_) for _ in card_used[:-1]])}")
        print(f"score: {score}")

        print()


if __name__ == "__main__":
    tmp = Game()
    tmp.new_game(mode='step', active_power=True)
    # # random player, avg.score = 98
    # tmp = Game()
    # score = 0
    # for i in tqdm(range(500)):
    #     score += tmp.new_game_quiet()
    # print(score/500)

    # tmp = Game()
    # score, save_data = tmp.new_game_quiet(is_save=True)
    # with open('0002.data', 'wb') as f:
    #     pickle.dump(save_data, f)
