import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key


# Symmetric encryption/decryption


def encrypt_message(aes_key, iv, data):
    """
    Encrypt message with symmetric AES key (PKCS7 padding)
    :param aes_key: AES key used in encryption
    :param iv: initialization vector used with the key
    :param data: message to be encrypted
    :return: encrypted message
    """
    cipher = Cipher(aes_key, modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    padded_data = padder.update(data) + padder.finalize()
    res = encryptor.update(padded_data) + encryptor.finalize()

    return res


def decrypt_message(aes_key, iv, data):
    """
    Decrypt message with symmetric AES key (PKCS7 padding)
    :param aes_key: AES key used in decryption
    :param iv: initialization vector used with the key
    :param data: encrypted message
    :return: decrypted message
    """
    cipher = Cipher(aes_key, modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()

    padded_data = decryptor.update(data) + decryptor.finalize()
    res = unpadder.update(padded_data) + unpadder.finalize()

    return res


# Key generation


def generate_symmetric_key(private_key, peer_public_key):
    """
    Generate symmetric AES key using ECDH
    :param private_key: host private key
    :param peer_public_key: public key of the peer
    """
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data', backend=default_backend()).derive(shared_key)
    aes_key = AES(derived_key)
    return aes_key


def generate_key():
    """
    Generate EC key
    :return: EllipticCurvePrivateKey and corresponding EllipticCurvePublicKey
    """
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
    return (private_key, private_key.public_key())


# Key encoding conversion


def key_to_bytes(public_key):
    """
    Convert key to ASN1 DER format bytes
    :param public_key: public key object
    :return: public key ASN1 DER bytes in PEM format
    """
    return public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


def bytes_to_key(public_key_hex):
    """
    Convert DER format bytes to hex
    :param public_key_hex: public key ASN1 DER in bytes
    :return: RSAPublicKey object
    """
    return serialization.load_der_public_key(public_key_hex, default_backend())


# Key saving


def save_key(pk, path):
    """
    Save key to .pem file
    :param pk: public key object to save
    :param path: path to .pem file to save
    """
    pem = pk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(path, 'wb') as pem_out:
        pem_out.write(pem)


def load_key(path):
    """
    Load key from .pem file
    :param path: path to .pem file
    :return: private key object
    """
    with open(path, 'rb') as pem_in:
        pemlines = pem_in.read()
    private_key = load_pem_private_key(pemlines, None, default_backend())
    return private_key