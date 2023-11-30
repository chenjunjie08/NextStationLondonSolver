class Node():
    def __init__(self, id: int) -> None:
        self.id = id                     # node id
        self.pos = [-1, -1]              # node position
        self.adj = []                    # adjacent nodes
        # station type, [4,3,5,0], [1,1,1,1] for central?
        self.sttn = [0, 0, 0, 0]
        self.is_trt = False              # is tourist
        self.dst = -1                    # node district

    def set_pos(self, line=None, column=None):
        if line is not None:
            self.pos[0] = line
        if column is not None:
            self.pos[1] = column

    def set_adj(self, node):
        if node in self.adj:
            return
        self.adj.append(node)
        node.adj.append(self)

    def set_sttn(self, sttn):
        if sttn == 5:
            self.sttn = [1, 1, 1, 1]
            return
        self.sttn[sttn-1] = 1

    def set_is_trt(self):
        self.is_trt = True

    def set_dst(self, dst):
        self.dst = dst

    @property
    def info(self):
        return {
            "id": self.id,
            "pos": self.pos,
            "sttn": self.sttn,
            "is_trt": self.is_trt,
            "dst": self.dst,
            "adj": [_.id for _ in self.adj]
        }
