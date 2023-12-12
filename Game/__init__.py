# import os
# import sys
# sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from gymnasium.envs.registration import register

register(
    id="NSL/NextStationLondon-v0",
    entry_point="Game.envs:NextStationLondonEnv",
)
