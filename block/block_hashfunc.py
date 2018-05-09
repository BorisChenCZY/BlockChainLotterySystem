import hashlib

def hash(info):
    return bytes(hashlib.sha3_512(info).hexdigest().encode("utf-8"))