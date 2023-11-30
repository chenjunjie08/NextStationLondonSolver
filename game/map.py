from node import Node
from connect import Connect


class Map():
    def __init__(self):
        self.nodes = {}
        self.connects = []

        # node generate
        node_pos = []
        with open('./game/node_pos.txt') as f:
            for line in f.readlines():
                node_pos.append(line.strip())
        self.map_h = len(node_pos)
        self.map_w = len(node_pos[0])

        # line, column, sttn
        idx = 0
        self.nodes_position = {}
        for idx_line, line in enumerate(node_pos):
            for idx_column, node in enumerate(line):
                if node != '0':
                    self.nodes[idx] = Node(idx)
                    self.nodes[idx].set_pos(idx_line, idx_column)
                    self.nodes[idx].set_sttn(int(node))
                    self.nodes_position[(idx_line, idx_column)] = idx
                    idx += 1

        # adjacent
        directions = [(-1, 1), (0, 1), (1, 1), (1, 0)]
        for idx in range(len(self.nodes)):
            begin_pos = self.nodes[idx].pos
            for direction in directions:
                current_pos = begin_pos.copy()
                while 0 <= current_pos[0] < self.map_h and 0 <= current_pos[1] < self.map_w:
                    tar_idx = self.nodes_position.get(tuple(current_pos))
                    if tar_idx is not None and tar_idx != idx:
                        self.nodes[idx].set_adj(self.nodes[tar_idx])
                        self.connects.append(
                            Connect(self.nodes[idx], self.nodes[tar_idx])
                        )
                        current_pos = [-1, -1]
                        continue
                    else:
                        current_pos[0] += direction[0]
                        current_pos[1] += direction[1]


if __name__ == "__main__":
    tmp = Map()
    print(tmp.nodes[25].info)
    print(tmp.nodes_position)
    print(len(tmp.connects))
