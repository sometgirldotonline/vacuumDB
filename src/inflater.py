# volumeDB inflater
import os
import struct
import random

def xor_obfuscate(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def return_obf_bloat(data, fake_chunks=2):
    if isinstance(data, str):
        payload = data.encode()
    else:
        payload = bytes(data)

    key = os.urandom(5)
    obf = xor_obfuscate(payload, key)

    buf = bytearray()

    buf += b"RCON"

    buf += b"KEYS"
    buf += struct.pack(">I", len(key))
    buf += key

    buf += b"TEXT"
    buf += struct.pack(">I", len(obf))
    buf += obf

    for _ in range(fake_chunks):
        size = random.randint(200_000, 800_000)
        buf += random.choice([b"IMGD", b"THMB", b"AUDD", b"CMPR"])
        buf += struct.pack(">I", size)
        buf += os.urandom(size)

    return bytes(buf)



def store_obf_bloat(filename, data, fake_chunks=2):
    if isinstance(data, str):
        payload = data.encode()
    else:
        payload = bytes(data)
    key = os.urandom(5)  # tiny key, very "obfuscation-style"
    obf = xor_obfuscate(payload, key)

    with open(filename, "wb") as f:
        f.write(b"RCON")  # fake "Resource Container"

        # key chunk (looks like metadata)
        f.write(b"KEYS")
        f.write(struct.pack(">I", len(key)))
        f.write(key)

        # payload chunk
        f.write(b"TEXT")
        f.write(struct.pack(">I", len(obf)))
        f.write(obf)

        # fake resource chunks
        for _ in range(fake_chunks):
            size = random.randint(200_000, 800_000)
            f.write(random.choice([b"IMGD", b"THMB", b"AUDD", b"CMPR"]))  # looks legit
            f.write(struct.pack(">I", size))
            f.write(os.urandom(size))

def retrieve_obf_bloat(filename):
    with open(filename, "rb") as f:
        if f.read(4) != b"RCON":
            raise ValueError("bad header")

        # read key chunk
        chunk = f.read(4)
        if chunk != b"KEYS":
            raise ValueError("missing key chunk")

        key_len = struct.unpack(">I", f.read(4))[0]
        key = f.read(key_len)

        # read until TEXT chunk
        while True:
            tag = f.read(4)
            if not tag:
                raise ValueError("TEXT chunk not found")

            size = struct.unpack(">I", f.read(4))[0]

            if tag == b"TEXT":
                encoded = f.read(size)
                break
            else:
                f.seek(size, os.SEEK_CUR)  # skip fake chunk

        return xor_obfuscate(encoded, key)
