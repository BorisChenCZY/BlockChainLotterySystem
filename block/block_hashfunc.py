import hashlib

def hash(info):
    return bytes(hashlib.sha3_256(info).hexdigest().encode("utf-8"))