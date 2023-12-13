import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import pdb
from game import Game
from card import Cards


class NextStationLondonEnv(gym.Env):

    def __init__(self):
        # observe connects, goals, round, color, card used, card, is_mid
        self.observation_space = spaces.Box(0, 1, shape=(
            155 * 5 + 5 + 4 + 4 + 11 + 11 + 1 + 156,), dtype=int)

        # We have 156 actions, corresponding to 155 connects and pass
        self.action_space = spaces.Discrete(156)

        self.game = Game()

        self.pass_reward = 0
        self.invalid_reward = 0

    def _get_obs(self):
        # connects
        obs_connects = np.zeros((155, 5))
        for idx in range(len(self.game.connects)):
            obs_connects[idx, self.game.connects[idx].color] = 1
        obs_connects = obs_connects.flatten()

        # goal used
        obs_goal = self.goals_used

        # round
        obs_round = np.zeros(4)
        obs_round[self.round] = 1

        # color
        obs_color = np.zeros(4)
        obs_color[self.color] = 1

        # card_used
        obs_card_used = np.zeros(11)
        obs_card_used[np.array(self.card_used)] = 1

        # card
        obs_card = np.zeros(11)
        obs_card[self.card_idx] = 1

        # is_mid
        obs_is_mid = np.zeros(1)
        obs_is_mid[0] = int(self.card.is_mid)

        # possible_move
        obs_possible_move = np.zeros(156)
        obs_possible_move[-1] = 1
        for begin in self.possible_move.keys():
            for end in self.possible_move[begin]:
                obs_possible_move[self.game.connect_search(
                    self.game.connects, begin, end)] = 1

        return np.concatenate([obs_connects, obs_goal, obs_round, obs_color,
                               obs_card_used, obs_card, obs_is_mid, obs_possible_move]).astype(int)

    def _get_info(self):
        return {
            "total_score": self.total_score,
            "possible_move": self.possible_move
        }

    def new_game_init(self):
        # init game
        self.game.__init__()

        # init round
        self.round = 0

        # init color
        self.colors = [0, 1, 2, 3]
        random.shuffle(self.colors)

        # init score
        self.total_score = 0
        self.river_score = np.array([0, 0, 0, 0])
        self.dst_score = np.array([0, 0, 0, 0])
        self.inter_score = np.array([0, 0, 0])
        self.trt_score = np.array([0, 1, 2, 4, 6, 8, 11, 14, 17, 21, 25])
        self.goals_score = np.array([0, 0, 0, 0, 0])

        # init goals
        self.goals_used = np.array([0, 0, 0, 0, 0])
        self.goals_used[np.random.choice([0, 1, 2, 3, 4], 2, False)] = 1

        # init goal-related var
        self.dsts_total = np.array([0 for _ in range(13)])
        self.trts_total = [9, 16, 19, 36, 49]
        self.cntr_total = [18, 19, 20, 25, 26, 30, 32, 33, 34]

    def new_round_init(self):
        # round start
        self.color = self.colors[self.round]

        # init heads, nodes, and connects
        self.heads = [self.game.nodes_head[self.color]]
        self.nodes = [self.game.nodes_head[self.color]]
        self.connects = []
        self.game.nodes[self.game.nodes_head[self.color]].set_color(self.color)

        # init new cards
        self.cards = Cards()
        self.card_used = []
        self.card_orders = [_ for _ in range(11)]
        random.shuffle(self.card_orders)

        # init dst
        self.dsts = np.array([0 for _ in range(13)])
        self.dsts[self.game.nodes[self.game.nodes_head[self.color]].dst] += 1

    def draw_a_card(self):
        self.card_idx = self.card_orders.pop(0)
        self.card_used.append(self.card_idx)
        if self.card_idx == 0:
            self.card_idx = self.card_orders.pop(0)
            self.card_used.append(self.card_idx)
            self.cards.cards[self.card_idx].set_is_mid()
        self.card = self.cards.cards[self.card_idx]
        self.cards.end_num += int(self.card.is_red)

    def get_possible_move(self):
        if self.card.is_mid:
            self.possible_move = self.game.possible_move(
                self.nodes, self.nodes, self.card.sttn)
        else:
            self.possible_move = self.game.possible_move(
                self.heads, self.nodes, self.card.sttn)

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # new_game
        self.new_game_init()

        # new round
        self.new_round_init()

        # draw
        self.draw_a_card()

        # possible move
        self.get_possible_move()

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(self, action):
        # pass
        if action == 155:
            if self.cards.end_num < 5:
                self.draw_a_card()
                self.get_possible_move()

                observation = self._get_obs()
                info = self._get_info()
                return observation, self.pass_reward, False, False, info

            if self.round == 3:
                observation = self._get_obs()
                info = self._get_info()
                return observation, self.pass_reward, True, False, info

            else:
                self.round += 1
                self.new_round_init()

                self.draw_a_card()
                self.get_possible_move()

                observation = self._get_obs()
                info = self._get_info()
                return observation, self.pass_reward, False, False, info

        # check if valid
        connect = self.game.connects[action]
        if connect.endpoint[0].id in self.possible_move.keys():
            begin = connect.endpoint[0].id
            end = connect.endpoint[1].id
        elif connect.endpoint[1].id in self.possible_move.keys():
            begin = connect.endpoint[1].id
            end = connect.endpoint[0].id
        else:
            observation = self._get_obs()
            info = self._get_info()
            return observation, self.invalid_reward, False, False, info

        if begin in self.possible_move.keys() and end in self.possible_move[begin]:
            # modify heads
            if len(self.heads) == 1:
                self.heads.append(end)
            elif not begin in self.heads:
                self.heads.append(end)
            else:
                for idx, head in enumerate(self.heads):
                    if head == begin:
                        self.heads[idx] = end
                        break

            # modify nodes
            self.nodes.append(end)

            self.dsts[self.game.nodes[end].dst] += 1
            self.dst_score[self.round] = self.game.score_dst(self.dsts)
            # goal 1
            if self.goals_score[1] == 0:
                self.dsts_total[self.game.nodes[end].dst] = 1
                if self.dsts_total.sum() == 13:
                    self.goals_score[1] == 1

            if self.game.nodes[end].is_trt:
                if len(self.trt_score) > 1:
                    self.trt_score = self.trt_score[1:]
                # goal 2
                if self.goals_score[2] == 0:
                    for idx, val in enumerate(self.trts_total):
                        if self.game.nodes[end].id == val:
                            self.trts_total.pop(idx)
                            break
                    if len(self.trts_total) == 0:
                        self.goals_score[2] = 1

            # goal 3
            if self.goals_score[3] == 0:
                for idx, val in enumerate(self.cntr_total):
                    if self.game.nodes[end].id == val:
                        self.cntr_total.pop(idx)
                        break
                if len(self.cntr_total) == 0:
                    self.goals_score[3] = 1

            self.game.nodes[end].set_color(self.color)
            if sum(self.game.nodes[end].color) < 2:
                pass
            elif sum(self.game.nodes[end].color) == 2:
                self.inter_score[0] += 1
            elif sum(self.game.nodes[end].color) == 3:
                self.inter_score[0] -= 1
                self.inter_score[1] += 1
            elif sum(self.game.nodes[end].color) == 4:
                self.inter_score[1] -= 1
                self.inter_score[2] += 1

            if len(self.nodes) == 2:
                if sum(self.game.nodes[begin].color) < 2:
                    pass
                elif sum(self.game.nodes[begin].color) == 2:
                    self.inter_score[0] += 1
                elif sum(self.game.nodes[begin].color) == 3:
                    self.inter_score[0] -= 1
                    self.inter_score[1] += 1
                elif sum(self.game.nodes[begin].color) == 4:
                    self.inter_score[1] -= 1
                    self.inter_score[2] += 1

            # goal 0
            if self.goals_score[0] == 0 and self.inter_score.sum() >= 8:
                self.goals_score[0] = 1

            # modify connects
            connect_id = self.game.connect_search(
                self.game.connects, begin, end)
            self.connects.append(connect_id)
            self.game.connects[connect_id].set_color(self.color)
            if self.game.connects[connect_id].is_cross_river:
                self.river_score[self.round] += 1
            # goal 4
            if self.goals_score[4] == 0 and self.river_score.sum() >= 6:
                self.goals_score[4] = 1

            self.game.connects[connect_id].set_unavailable()
            for idx in range(len(self.game.connects)):
                if idx == connect_id:
                    continue
                if not self.game.connects[idx].is_available:
                    continue
                if self.game.connects[connect_id].is_intersect(self.game.connects[idx]):
                    self.game.connects[idx].set_unavailable()

            total_score = self.game.score_total(
                self.river_score, self.dst_score, self.trt_score, self.inter_score, self.goals_score, self.goals_used)
            reward = total_score - self.total_score
            self.total_score = total_score

            if self.cards.end_num < 5:
                self.draw_a_card()
                self.get_possible_move()

                observation = self._get_obs()
                info = self._get_info()
                return observation, reward, False, False, info

            if self.round == 3:
                observation = self._get_obs()
                info = self._get_info()
                return observation, reward, True, False, info

            else:
                self.round += 1
                self.new_round_init()

                self.draw_a_card()
                self.get_possible_move()

                observation = self._get_obs()
                info = self._get_info()
                return observation, reward, False, False, info

        else:
            observation = self._get_obs()
            info = self._get_info()
            return observation, self.invalid_reward, False, False, info


def auto_test():
    game = NextStationLondonEnv()
    game.reset()
    info = game._get_info()
    total_reward = 0

    while True:
        possible_move = info['possible_move']
        if len(possible_move) == 0:
            action = 155
        else:
            # begin = random.choice(list(possible_move.keys()))
            # end = random.choice(possible_move[begin])
            # action = game.game.connect_search(game.game.connects, begin, end)
            action = random.choice([_ for _ in range(156)])
        obs, reward, terminate, trunction, info = game.step(action)
        total_score = info['total_score']
        if terminate:
            print(total_score)
            break


if __name__ == '__main__':
    auto_test()
