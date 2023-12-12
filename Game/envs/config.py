# game config
class Config():
    def __init__(self, config=None):
        if config is None:
            self.use_goals = False

            # whether use pencil abilities
            self.use_pencil = False

            # use random cards or fixed cards
            self.fixed_set = False
            self.cards = None
            self.goals = None
            self.pencils = None

        else:
            self.use_goals = config['use_goals']

            self.use_pencil = config['use_pencil']

            self.fixed_set = config['fixed_set']
            if self.fixed_set:
                self.cards = config['cards']
                if self.use_goals:
                    self.goals = config['goals']
                if self.use_pencil:
                    self.pencils = config['pencils']
