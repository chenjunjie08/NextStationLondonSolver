class Connect():
    def __init__(self, node1, node2):
        self.endpoint = []                  # two endpoints
        self.set_endpoint(node1, node2)
        self.is_cross_river = False         # is the connect cross river
        self.color = [0, 0, 0, 0]           # connect color
        self.is_available = True            # is the connect available?

    def set_endpoint(self, node1, node2):
        # node with lower id at first place
        if node1.id < node2.id:
            self.endpoint = [node1, node2]
        else:
            self.endpoint = [node2, node1]

    def set_cross_river(self):
        self.is_cross_river = True

    def set_color(self, color):
        for i in range(4):
            self.color[i] = 0
        self.color[color] = 1

    def set_unavailable(self):
        self.is_available = False

    def info(self):
        try:
            return {
                "endpoint": [self.endpoint[0].id, self.endpoint[1].id],
                "color": self.color
            }
        except:
            print("Connect not defined!")
