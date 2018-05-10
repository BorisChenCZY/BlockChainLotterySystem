import hashlib

def hash(info):
    return hashlib.sha3_256(info).hexdigest()