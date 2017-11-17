class Messenger:
    def send_prepare(self, proposal_id):
        pass

    def send_promise(self, proposer_uid, proposal_id, previous_id, accepted_val):
        pass

    def send_accept(self, proposal_id, proposal_val):
        pass

    def send_accepted(self, proposal_id, accepted_val):
        pass


class Proposer:
    def __init__(self, uid):
        self.uid = uid
        self.leader = False

        self.proposal_id = None
        self.proposal_val = None
        self.next_proposal_num = 1

        self.last_accepted_id = None

    def set_proposal(self, val):
        if self.proposal_val = None:
            self.proposal_val = val

    def send_prepare(self, proposal_id):
        data = ["prepare", proposal_id]
        send_data_to_all(data)

    def prepare(self):
        self.proposal_id = (self.next_proposal_id, self.uid)
        self.next_proposal_num += 1
        self.recv_promises = set()
        send_prepare(self.proposal_id)

    def start_election(self):
        ballot_num = (self.proposal_id, self.uid)
        data = ["prepare", ballot_num]
        send_data_to_all(data)

    def recv_promise(self, promise):
        if promised_id != self.proposal_id:
            return

        self.recv_promises.add(promise.uid)

        if promise.prev_accepted_id > self.last_accepted_id:
            # An acceptor has already accepted a val
            self.proposal_val = promise.prev_accepted_id

        if len(self.recv_promises) > self.quorum_size:
            data = ["accept", self.proposal_id, self.proposal_val]
            send_data_to_all(data)

    def accept_leader(self):
        '''After received ack from majority'''
        if self.received_val = None:
            data = ["accept", ballot_num, self.proposal_val]
            send_data_to_all(data)


class Acceptor:
    def __init__(self):
        self.promised_id = None
        self.accepted_num = None
        self.accepted_val = None

    def accept_proposal(uid, proposal_id):
        data = [uid, proposal_id, self.accepted_num, self.accepted_val]
        send_data(data)

    def recv_proposal(self, uid, proposal_id):
        if self.promised_id = None:
            self.promised_id = proposal_id
            self.accept_proposal(uid, proposal_id)

    def recv_accept_prepare(self, uid, proposal_id, val):
        pass


class Learner:
    def __init__(self):
        pass


class Node(Proposer, Acceptor, Learner):
    '''Each node performs all roles'''
    def __init__(self):
        pass
