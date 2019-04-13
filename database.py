def db_find(clients, UID):
    for c in clients:
        if c.UID == UID:
            return c
    return None

def db_update(clients, client):
    for i,c in enumerate(clients):
        if c.UID == client.UID:
            clients[i] = client
            break
    return clients

def db_print(clients):
    for c in clients:
        print(f'Client: {c.UID}. IK: {c.IK}, SPK: {c.SPK}, SIG: {c.SIG}, OPK1: {c.OPK1}, OPK2: {c.OPK2}, OPK3: {c.OPK3}, OPK4: {c.OPK4}, OPK5: {c.OPK5}')

class Client:
    def __init__(self, UID, IK, SPK, SIG, OPK1, OPK2, OPK3, OPK4, OPK5):
        self.UID = UID
        self.IK = IK
        self.SPK = SPK
        self.SIG = SIG
        self.OPK1 = OPK1
        self.OPK2 = OPK2
        self.OPK3 = OPK3
        self.OPK4 = OPK4
        self.OPK5 = OPK5

