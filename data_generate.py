from game.game import Game
import pickle
from tqdm import tqdm
import os

data_num = 5000
save_dir = '../../DATA/NextStationLondon/231212_randomActor'
os.makedirs(save_dir, exist_ok=True)

tmp = Game()
for idx in tqdm(range(data_num)):
    score, save_data = tmp.new_game_quiet(is_save=True)
    file_name = f"{idx:06d}.data"
    with open(os.path.join(save_dir, file_name), 'wb') as f:
        pickle.dump(save_data, f)
