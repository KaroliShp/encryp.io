from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

import os

# Cryptography

def generate_symmetric_key(private_key, peer_public_key):
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data', backend=default_backend()).derive(shared_key)
    aes_key = AES(derived_key)
    return aes_key

def encrypt_message(aes_key, iv, data):
    cipher = Cipher(aes_key, modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    padded_data = padder.update(data) + padder.finalize()
    res = encryptor.update(padded_data) + encryptor.finalize()

    return res

def decrypt_message(aes_key, iv, data):
    cipher = Cipher(aes_key, modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()

    padded_data = decryptor.update(data) + decryptor.finalize()
    res = unpadder.update(padded_data) + unpadder.finalize()

    return res

def generate_key():
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
    return (private_key, private_key.public_key())

# Key display

def key_to_bytes(public_key):
    return public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

def bytes_to_key(public_key_hex):
    return serialization.load_der_public_key(public_key_hex, default_backend())

# Key saving

def save_key(pk, filename):
    pem = pk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)

def load_key(filename):
    with open(filename, 'rb') as pem_in:
        pemlines = pem_in.read()
    private_key = load_pem_private_key(pemlines, None, default_backend())
    return private_key

"""
if __name__ == "__main__":
    pr1, _ = generate_key()
    save_key(pr1, 'klevas_key.pem')
    pr2, _ = generate_key()
    save_key(pr2, 'berzas_key.pem')

    pr1, pb1 = generate_key()
    pr2, pb2 = generate_key()

    k1 = generate_symmetric_key(pr1, pb2)
    k2 = generate_symmetric_key(pr2, pb1)

    iv = os.urandom(16)

    e1 = encrypt_message(k1, iv, b"Labas")
    d1 = decrypt_message(k2, iv, e1)

    e2 = encrypt_message(k2, iv, b"Labas")
    d2 = decrypt_message(k1, iv, e2)
"""

"""
# Generate ECDH private key
private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())

print(private_key.key_size) # bits

# Other public key
peer_private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())

# Shared secret
shared_key = private_key.exchange(ec.ECDH(), peer_private_key.public_key())
shared_key2 = peer_private_key.exchange(ec.ECDH(), private_key.public_key())

print(shared_key.hex())
print(shared_key2.hex())

# Derive key using key derivation function (KDF) based on HMAC
derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data', backend=default_backend()).derive(shared_key)
derived_key_2 = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data', backend=default_backend()).derive(shared_key2)

aes_key = AES(derived_key)
print(aes_key.key.hex())
print(aes_key.key_size)

iv = os.urandom(16) # Random 16 bytes IV
cipher = Cipher(aes_key, modes.CBC(iv), backend=default_backend())
encryptor = cipher.encryptor()
decryptor = cipher.decryptor()

data = b"a secret message"
ct = encryptor.update(data) + encryptor.finalize()
dt = decryptor.update(ct) + decryptor.finalize()
print(data == dt)
"""