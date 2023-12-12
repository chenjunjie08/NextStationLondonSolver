import gymnasium as gym
import Game

env = gym.make("NSL/NextStationLondon-v0")
env = gym.wrappers.RecordEpisodeStatistics(env)
