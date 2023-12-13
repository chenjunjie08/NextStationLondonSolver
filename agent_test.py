import gymnasium as gym
from Agents.ppo_agent import PPO_Agent
import torch
import pdb
import numpy as np
from tqdm import tqdm
import Game


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
    env = gym.make("NSL/NextStationLondon-v0")
    agent = PPO_Agent(env)
    agent.load('./checkpoints/PPO_test_1_1702462709.pth')
    agent.cuda()

    auto_test(env, agent, 100)
