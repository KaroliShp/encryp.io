"""
Implementation for hackathon purposes
"""

class Database:

    def __init__(self, clients_list):
        """
        Database for clients
        :param clients_list: list of ClientModel objects
        """
        self._clients_list = clients_list


    def get_clients_list(self):
        return self._clients_list


    def find_client_by_uid(self, uid):
        """
        Find client by their UID
        :param uid: client UID
        :return: client object if found, else None
        """
        for client in self._clients_list:
            if client.get_uid() == uid:
                return client
        return None


    def update_client(self, new_client):
        """
        Update client information
        :param new_client: new client object of ClientModel
        """
        for i, client in enumerate(self._clients_list):
            if client.get_uid() == new_client.get_uid():
                self._clients_list[i] = new_client
                break


    def db_print(self, clients):
        """
        Print all clients
        """
        for client in self._clients_list:
            print(f'Client: {client.get_uid()}. IK: {client.get_ik()}')