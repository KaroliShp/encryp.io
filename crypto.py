from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers import Cipher, modes

import os

# Generate ECDH private key
private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())

print(private_key.key_size) # bits

# Other public key
peer_public_key = ec.generate_private_key(ec.SECP384R1(), default_backend()).public_key()

# Shared secret
shared_key = private_key.exchange(ec.ECDH(), peer_public_key)

# Derive key using key derivation function (KDF) based on HMAC
derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data', backend=default_backend()).derive(shared_key)

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