class Proposer:
    def __init__(self, uid):
        self.uid = uid
        self.leader = False
        self.proposal_id = None
        self.proposal_val = None

    def set_proposal(self, val):
        if self.proposal_val = None:
            self.proposal_val = val


class Acceptor:
    def __init__(self):
        pass


class Learner:
    def __init__(self):
        pass


class Node(Proposer, Acceptor, Learner):
    '''Each node performs all roles'''
    def __init__(self):
        pass
