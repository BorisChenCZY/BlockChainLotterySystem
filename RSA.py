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

if __name__ == '__main__':
    # pubkey, privkey = get_keys()
    # save(pubkey, 'pub.pem')
    # save(privkey, 'priv.pem')
    pubkey = load("pub.pem", 0)
    privkey = load("priv.pem", 1)
    # print(sign("Hello".encode("utf-8"), privkey))
    # print(bytes(bytearray.fromhex("0d92b2f4c8a0e1313762e0894cd0e7d907b136baf252eb2964771e83be1367ec8a2df9c9cf730ab418b28d92c6a49c264bfc412df51f1e236cb2f6312cc6e256")))
    sign = "3b8581f6325adccfbde005d1996b5b866e9ed76b9ecbc24c5fac50e2ef1bf32934e554f4c7917219178628549d824506ab2e30b4308d36d7ada2c5d4fc2053ed"
    print(verify("hello".encode('utf-8'), bytes(bytearray.fromhex(sign)), pubkey))

