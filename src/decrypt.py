import base64
import random

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

backend = default_backend()

SEPARATOR = ":"
DATA_1 = "data.1"
DATA_2 = "data.2"


def derive_key(
    passphrase: str, salt: bytes, iterations: int = 100000
) -> bytes:
    """Derive a key from the passphrase using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=backend,
    )
    return kdf.derive(passphrase.encode())


def decrypt_master_key(
    encrypted_master_key: bytes, passphrase: str, salt: bytes
) -> bytes:
    """Decrypt the master key using the passphrase-derived key."""
    key = derive_key(passphrase, salt)
    iv = encrypted_master_key[:16]
    encrypted_key = encrypted_master_key[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_master_key = decryptor.update(encrypted_key) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    master_key = unpadder.update(padded_master_key) + unpadder.finalize()
    return master_key


def decrypt_data(encrypted_data: bytes, master_key: bytes) -> bytes:
    """Decrypt data using the master key."""
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(master_key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data


def get_salt() -> bytes:
    """Get a fixed salt(16)."""
    return b"\x10\xbc\xb8\xbf3\xcfJ}\x1c8I\xf3\x8995{"


def unscramble_raw_lines(scrambled_data: bytes) -> list[bytes]:
    """Unscramble the scrambled data into raw lines."""
    raw_lines: list[bytes] = []
    i = 0
    while i < len(scrambled_data):
        line_length: int = scrambled_data[i]
        i += 1
        line: bytes = scrambled_data[i:i + line_length]
        raw_lines.append(line + b"\n")
        i += line_length
    return raw_lines[::-1]


def read_master_key_dict_from_file(filename: str) -> dict[str, bytes]:
    """Read the master key dictionary from a file."""
    master_key_dict: dict[str, bytes] = {}
    with open(filename, "rb") as fd:
        lines: list[bytes] = unscramble_raw_lines(fd.read())
        for line in lines:
            line_str: str = base64.b64decode(line).decode()
            passphrase, hased_master_key = line_str.split(SEPARATOR)
            encrypted_master_key: bytes = base64.b64decode(hased_master_key.encode())
            master_key_dict[passphrase] = encrypted_master_key
    return master_key_dict


def read_encrypted_data_from_file(filename: str) -> bytes:
    """Read the encrypted data from a file."""
    with open(filename, "rb") as fd:
        return fd.read()


def restore_data(data: bytes) -> str:
    cycles, h = base64.b64decode(data).decode().split(SEPARATOR)
    data = h.encode()
    for _ in range(int(cycles)):
        data = base64.b64decode(data)
    return data.decode()


def get_data() -> str:
    salt: bytes = get_salt()
    passphrase: str = random.SystemRandom().choice(
        [str(i) for i in range(1000)]
    )
    encrypted_master_keys: dict[str, bytes] = read_master_key_dict_from_file(
        DATA_1
    )
    encrypted_data: bytes = read_encrypted_data_from_file(DATA_2)
    decrypted_master_key: bytes = decrypt_master_key(
        encrypted_master_keys[passphrase], passphrase, salt
    )
    return restore_data(decrypt_data(encrypted_data, decrypted_master_key))
