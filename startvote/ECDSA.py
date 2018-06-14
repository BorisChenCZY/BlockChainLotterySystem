from ecpy.curves     import Curve,Point
from ecpy.keys       import ECPublicKey, ECPrivateKey
from ecpy.ecdsa      import ECDSA
import hashlib
import binascii
import settings

# blind signature
cv = Curve.get_curve('secp256k1')
signer = ECDSA()
pv_key = ECPrivateKey(int(hashlib.md5(settings.PRIVATE_KEY.encode()).hexdigest(), 16),
                          cv)
pu_key = pv_key.get_public_key()
d = pv_key.d
P = pu_key.W
n = cv.order
G = cv.generator
r = 1
R = r*G
hasher = hashlib.sha256()

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')

def hex_to_bytes(x):
    x = int(x, 16)
    return int_to_bytes(x)

def bytes_to_hex(x):
    x = int.from_bytes(x, "big")
    return hex(x)

## c is hexstring
def blind_signature(c_):
    c_ = int(c_, 16)
    s_ = (r - c_ * d) % n
    return hex(s_)

## m, c, s are hexstring
def blind_verify(m, c, s):
    c = int(c, 16)
    s = int(s, 16)
    print("t",  str(hex((c * P + s * G).x % n))[2:])
    print("m", str(m))
    hasher.update((str(m) + str(hex((c * P + s * G).x % n))[2:]).encode())
    print(hex(int(hasher.hexdigest(), 16)%n))
    print("c:", hex(c))
    return hex(c) == hex(int(hasher.hexdigest(), 16)%n)

##prv, msg are string
def normal_signature(msg, prv):
    prv_key = ECPrivateKey(int(hashlib.md5(prv.encode()).hexdigest(), 16), cv)
    msg = msg.encode()
    sig = signer.sign(msg, prv_key)
    return hex(int.from_bytes(sig,"big"))

##all parameters are hexstring
def normal_verify(msg, sig, pub):
    pub = int_to_bytes(int(pub,16))
    pub_key = ECPublicKey(cv.decode_point(pub))
    msg = msg.encode()
    sig = int_to_bytes(int(sig, 16))
    return signer.verify(msg, sig, pub_key)
    
if __name__ == "__main__":
    try:
        msg = "{I am mark}"
        sig = normal_signature(msg, settings.PRIVATE_KEY)
        assert (normal_verify(msg, sig, settings.PUBLIC_KEY))
        print("Assertion ok")
        
        pv = ECPrivateKey(int(hashlib.md5("Mark111".encode()).hexdigest(), 16),
                          cv)
        pb = pv.get_public_key()
        
        gama = 2
        delta = 3
        A = R + gama * G + delta * P
        t = A.x
        Bpub = bytes_to_hex(cv.encode_point(pb.W))
        print("t:", hex(t))
        print("mypub:", Bpub)
        hasher.update((str(Bpub)[2:] + str(hex(t))[2:]).encode())
        c = hasher.hexdigest()
        print("c:", c)
        print("cmod:", hex(int(c, 16) % n))
        c_ = (int(c, 16) - delta) % n
        print(hex(c_))
        s_ = blind_signature(hex(c_))
        print(s_)
        s = (int(s_, 16) + gama) % n
        print(hex(s))
    finally:
        pass


#
# A = R + gama * G + delta * P
# t = A.x % n
# hexmsg = hex(int.from_bytes(msg, 'big'))
# hasher.update((str(hexmsg)[2:] + str(hex(t))[2:]).encode())
#
# print(hex(int(hasher.hexdigest(), 16)))
# c = int(hasher.hexdigest(), 16) % n
# print("c:", hex(c))
# c_ = (c - delta) % n
# print("c_:", c_)
#
# print("s_:", s_)
# print("sign:", int.from_bytes(signer.sign(int_to_bytes(c_), pv_key), 'big') % n)
# s = (s_ + gama) % n
# print("s:", s)
# print((c * P + s * G))
# print(t == (c * P + s * G).x % n)
# print(signer.verify(int_to_bytes(c_), int_to_bytes(s_), pu_key))