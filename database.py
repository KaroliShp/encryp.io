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
        print(f'Client: {c.UID}. IK: {c.IK}')

class Client:
    def __init__(self, UID, IK):
        self.UID = UID
        self.IK = IK