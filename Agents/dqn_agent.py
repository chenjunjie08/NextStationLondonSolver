import os
import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical
import numpy as np
import pdb


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class DQN_Agent(nn.Module):
    def __init__(self, env):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(np.array(env.observation_space.shape).prod(), 240),
            nn.ReLU(),
            nn.Linear(240, 168),
            nn.ReLU(),
            nn.Linear(168, env.action_space.n),
        )

    def load(self, ckpt_path):
        checkpoint = torch.load(ckpt_path)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.eval()

    def get_action_and_value(self, x, action=None):
        q_values = self.network(x.float())
        q_values = q_values * x[:, -157:].float()
        actions = torch.argmax(q_values, dim=1)
        if q_values.max() == 0:
            actions = torch.zeros_like(actions) + 155
        return actions
