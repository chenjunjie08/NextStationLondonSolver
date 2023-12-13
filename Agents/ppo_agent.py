import os
import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical
import numpy as np


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class PPO_Agent(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.critic = nn.Sequential(
            layer_init(
                nn.Linear(np.array(envs.observation_space.shape).prod(), 128)),
            nn.Tanh(),
            layer_init(nn.Linear(128, 128)),
            nn.Tanh(),
            layer_init(nn.Linear(128, 1), std=1.0),
        )
        self.actor = nn.Sequential(
            layer_init(
                nn.Linear(np.array(envs.observation_space.shape).prod(), 128)),
            nn.Tanh(),
            layer_init(nn.Linear(128, 128)),
            nn.Tanh(),
            layer_init(nn.Linear(128, envs.action_space.n), std=0.01),
        )

    def load(self, ckpt_path):
        checkpoint = torch.load(ckpt_path)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.eval()

    def get_value(self, x):
        return self.critic(x)

    def get_action_and_value(self, x, action=None):
        logits = self.actor(x)
        mask = x[:, -156:]
        logits = logits - (1 - mask) * 20
        probs = Categorical(logits=logits)
        if action is None:
            action = probs.sample()
        return action
        # , probs.log_prob(action), probs.entropy(), self.critic(x)
