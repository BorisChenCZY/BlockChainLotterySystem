import rsa

KEY_SIZE = 512
SIGN_HASH = 'SHA-1'

def get_keys():
    """
    :return: (pubkey, privkey)
    """
    return rsa.newkeys(KEY_SIZE)

def sign(message, private):
    return rsa.sign(message, private, SIGN_HASH)

def verify(message, signiture, publickey):
    return rsa.verify(message, signiture, publickey)

def save(key, filepath):
    content = key.save_pkcs1()
    with open(filepath, 'wb') as f:
        f.write(content)

def load(filepath, type):
    """
    :str filepath: the path of loading file
    :int type: 0 for public key, 1 for priviate key
    :return: corresponding key to type
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    if(type == 0):
        return rsa.PublicKey.load_pkcs1(content)
    else:
        return rsa.PrivateKey.load_pkcs1(content)