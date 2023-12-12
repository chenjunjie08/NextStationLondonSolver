# cross_product
def cp(p1, p2, p3):
    return (p2[0]-p1[0])*(p3[1]-p1[1])-(p3[0]-p1[0])*(p2[1]-p1[1])


class Connect():
    def __init__(self, node1, node2):
        self.endpoint = []                  # two endpoints
        self.set_endpoint(node1, node2)
        self.is_cross_river = False         # is the connect cross river
        self.color = 0                      # connect color
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
        self.color = color

    def set_unavailable(self):
        self.is_available = False

    def is_intersect(self, connect=None, pos1=None, pos2=None):
        p1 = self.endpoint[0].pos
        p2 = self.endpoint[1].pos
        # Use connect first. If connect is not given, then use pos.
        if connect is not None:
            p3 = connect.endpoint[0].pos
            p4 = connect.endpoint[1].pos
        else:
            p3 = pos1
            p4 = pos2

        return cp(p1, p2, p3) * cp(p1, p2, p4) < 0 and cp(p3, p4, p1) * cp(p3, p4, p2) < 0

    @property
    def info(self):
        return {
            "endpoint": [self.endpoint[0].id, self.endpoint[1].id],
            "color": self.color
        }
