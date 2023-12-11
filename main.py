from game.game import Game
import copy
import random


def act(game, situation, begin, end):
    # unpack
    goals_used = situation['goals_used']

    round = situation['round']
    color = situation['color']

    heads = situation['heads']
    nodes = situation['nodes']
    connects = situation['connects']
    dsts = situation['dsts']

    total_score = situation['total_score']
    river_score = situation['river_score']
    dst_score = situation['dst_score']
    inter_score = situation['inter_score']
    trt_score = situation['trt_score']
    goals_score = situation['goals_score']

    dsts_total = situation['dsts_total']
    trts_total = situation['trts_total']
    cntr_total = situation['cntr_total']

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

    dsts[game.nodes[end].dst] += 1
    dst_score[round] = game.score_dst(dsts)
    # goal 1
    if goals_score[1] == 0:
        dsts_total[game.nodes[end].dst] = 1
        if dsts_total.sum() == 13:
            goals_score[1] == 1

    if game.nodes[end].is_trt:
        if len(trt_score) > 1:
            trt_score = trt_score[1:]
        # goal 2
        if goals_score[2] == 0:
            for idx, val in enumerate(trts_total):
                if game.nodes[end].id == val:
                    trts_total.pop(idx)
                    break
            if len(trts_total) == 0:
                goals_score[2] = 1

    # goal 3
    if goals_score[3] == 0:
        for idx, val in enumerate(cntr_total):
            if game.nodes[end].id == val:
                cntr_total.pop(idx)
                break
        if len(cntr_total) == 0:
            goals_score[3] = 1

    game.nodes[end].set_color(color)
    if sum(game.nodes[end].color) < 2:
        pass
    elif sum(game.nodes[end].color) == 2:
        inter_score[0] += 1
    elif sum(game.nodes[end].color) == 3:
        inter_score[0] -= 1
        inter_score[1] += 1
    elif sum(game.nodes[end].color) == 4:
        inter_score[1] -= 1
        inter_score[2] += 1

    if len(nodes) == 2:
        if sum(game.nodes[begin].color) < 2:
            pass
        elif sum(game.nodes[begin].color) == 2:
            inter_score[0] += 1
        elif sum(game.nodes[begin].color) == 3:
            inter_score[0] -= 1
            inter_score[1] += 1
        elif sum(game.nodes[begin].color) == 4:
            inter_score[1] -= 1
            inter_score[2] += 1

    # goal 0
    if goals_score[0] == 0 and inter_score.sum() >= 8:
        goals_score[0] = 1

    # modify connects
    connect_id = game.connect_search(game.connects, begin, end)
    connects.append(connect_id)
    if game.connects[connect_id].is_cross_river:
        river_score[round] += 1
    # goal 4
    if goals_score[4] == 0 and river_score.sum() >= 6:
        goals_score[4] = 1

    game.connects[connect_id].set_unavailable()
    for idx in range(len(game.connects)):
        if idx == connect_id:
            continue
        if not game.connects[idx].is_available:
            continue
        if game.connects[connect_id].is_intersect(game.connects[idx]):
            game.connects[idx].set_unavailable()

    total_score = game.score_total(
        river_score, dst_score, trt_score, inter_score, goals_score, goals_used)
    return total_score


def greedy(game, situation):
    possible_move = situation['possible_move']
    top_score = 0
    action = []

    if len(possible_move) == 0:
        return 'pass'

    for begin in possible_move.keys():
        for end in possible_move[begin]:
            score = act(copy.deepcopy(
                game), copy.deepcopy(situation), begin, end)
            if score == top_score:
                action.append(f"{begin}-{end}")
            elif score > top_score:
                action = [f"{begin}-{end}"]

    return random.choice(action)


if __name__ == "__main__":
    # greedy player, avg.score=99
    tmp = Game()
    score = 0
    for i in range(500):
        score += tmp.new_game(mode='random', auto_play=True, actor=greedy)
    print(score/500)
