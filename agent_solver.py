import gymnasium as gym
from Agents.ppo_agent import PPO_Agent
import torch
import pdb
import numpy as np
from tqdm import tqdm
import Game
from Game.envs.game import Game


def game_get_obs(game, situation):
    # connects
    obs_connects = np.zeros((155, 5))
    for idx in range(len(game.connects)):
        obs_connects[idx, game.connects[idx].color] = 1
    obs_connects = obs_connects.flatten()

    # goal used
    obs_goal = situation['goals_used']

    # round
    obs_round = np.zeros(4)
    obs_round[situation['round']] = 1

    # color
    obs_color = np.zeros(4)
    obs_color[situation['color']] = 1

    # card_used
    obs_card_used = np.zeros(11)
    obs_card_used[np.array(situation['card_used'])] = 1

    # card
    obs_card = np.zeros(11)
    obs_card[situation['card_idx']] = 1

    # is_mid
    obs_is_mid = np.zeros(1)
    obs_is_mid[0] = int(situation['card'].is_mid)

    # possible_move
    obs_possible_move = np.zeros(156)
    obs_possible_move[-1] = 1
    possible_move = situation['possible_move']
    for begin in possible_move.keys():
        for end in possible_move[begin]:
            obs_possible_move[game.connect_search(
                game.connects, begin, end)] = 1

    return np.concatenate([obs_connects, obs_goal, obs_round, obs_color,
                           obs_card_used, obs_card, obs_is_mid, obs_possible_move]).astype(int)


def agent_solver(agent, obs, game, possible_move):
    obs_tensor = torch.Tensor(obs).unsqueeze(0).cuda()
    action = agent.get_action_and_value(obs_tensor).cpu()

    if action == 155:
        return 'pass'

    connect = game.connects[action]
    if connect.endpoint[0].id in possible_move:
        begin = connect.endpoint[0].id
        end = connect.endpoint[1].id
    else:
        begin = connect.endpoint[1].id
        end = connect.endpoint[0].id
    return f"{begin}-{end}"


def actor(game, situation):
    return agent_solver(agent, game_get_obs(game, situation), game, situation['possible_move'])


if __name__ == '__main__':
    agent = PPO_Agent(gym.make("NSL/NextStationLondon-v0"))
    agent.load('./checkpoints/PPO_test_1_1702462709.pth')
    agent.cuda()

    game = Game()
    game.new_game(mode='step', auto_play=True, actor=actor)
