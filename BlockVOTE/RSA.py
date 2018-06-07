from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives import hashes
import binascii

PUB_KEY = 0
PRIV_KEY = 1


class RSAError(Exception):
    pass


def load(content, t):
    if type(content) != bytes:
        raise RSAError("content must be bytes")
    if t == PUB_KEY:
        key = load_pem_public_key(content, default_backend())
        if not isinstance(key, rsa.RSAPublicKey):
            raise RSAError("Type not right.")
    elif t == PRIV_KEY:
        key = load_pem_private_key(content, default_backend())
        if not isinstance(key, rsa.RSAPrivateKey):
            raise RSAError("Type not right")
    else:
        raise RSAError("Type not found")

    return key

def verify(msg, pubkey, sig):
    if not isinstance(pubkey, rsa.RSAPublicKey):
        raise RSAError("pubkey must be RSA public key!")
    pubkey.verify(sig, msg, padding=padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=0), algorithm=hashes.SHA1())
    return True

def sign(msg, privkey):
    if type(msg) is not bytes:
        raise RSAError("msg must be bytes")
    if not isinstance(privkey, rsa.RSAPrivateKey):
        raise RSAError("privkey must be RSA privite key!")
    # print(isinstance(hashes.SHA1, hashes.HashAlgorithm))
    return privkey.sign(msg, padding=padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=0), algorithm=hashes.SHA1())

def get_pair():
    priv = rsa.generate_private_key(65537, 512, default_backend())
    pub = priv.public_key()
    return pub, priv


if __name__ == '__main__':
    pub, priv = get_pair()
    # help(padding)
    sig = sign("Hello".encode('utf-8'), priv)
    by = binascii.hexlify(sig)
    sig = bytes(bytearray.fromhex(by.decode('utf-8')))
    print(verify("Hello".encode('utf-8'), pub, sig))

