import hashlib

def hash(info):
    return hashlib.sha3_512(info).hexdigest()