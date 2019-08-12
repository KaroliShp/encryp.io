"""
Implementation for hackathon purposes
"""

class ClientModel:

    def __init__(self, uid, ik):
        """
        Client model
        :param uid: client UID
        :param ik: client public key
        """
        self._uid = uid
        self._ik = ik

    
    def get_uid(self):
        return self._uid

    
    def get_ik(self):
        return self._ik