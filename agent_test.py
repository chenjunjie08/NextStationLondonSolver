import gymnasium as gym
from Agents.ppo_agent import PPO_Agent
from Agents.dqn_agent import DQN_Agent
import torch
import pdb
import numpy as np
from tqdm import tqdm
import Game
import random


def auto_test(env, agent, N=50):
    res = []
    for _ in tqdm(range(N)):
        obs, info = env.reset()

        while True:
            obs_tensor = torch.Tensor(obs).unsqueeze(0).cuda()
            action = agent.get_action_and_value(obs_tensor).cpu()
            obs, _, terminate, _, info = env.step(action)
            total_score = info['total_score']
            if terminate:
                res.append(total_score)
                break

    print(f"avg score is: {np.mean(res)}")


if __name__ == '__main__':
    seed = 0
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    env = gym.make("NSL/NextStationLondon-v0")
    env.unwrapped.set_active_power(True)

    # PPO
    agent = PPO_Agent(env)
    agent.load('./checkpoints/PPO_PPO_1_1702904622.pth')
    agent.cuda()

    # # DQN
    # agent = DQN_Agent(env)
    # agent.load('./checkpoints/DQN_DQN_1_1702473994.pth')
    # agent.cuda()

    auto_test(env, agent, 100)
