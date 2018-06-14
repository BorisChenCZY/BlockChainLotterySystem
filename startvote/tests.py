from ecpy.curves     import Curve,Point
from ecpy.keys       import ECPublicKey, ECPrivateKey
from ecpy.ecdsa      import ECDSA
import hashlib
import settings

# blind signature
cv = Curve.get_curve('secp256k1')
pv_key = ECPrivateKey(int(hashlib.md5("Mark".encode()).hexdigest(), 16),
                      cv)
pu_key = pv_key.get_public_key()

msg = "mark".encode()
signer = ECDSA()
sig = signer.sign(msg, pv_key)
print(int.from_bytes(sig, 'big'))
assert (signer.verify(msg, signer.sign(msg, pv_key), pu_key))

hasher = hashlib.sha512()
gama = 80
delta = 99
r = 30
P = pu_key.W
d = pv_key.d
n = pv_key.curve.order
G = pv_key.curve.generator
R = G
print("R:", R)
A = R + gama * G + delta * pu_key.W
print("A", A)
t = A.x % n
print("t:", t)
hasher.update(msg + t.to_bytes(32, 'big'))
c = int(hasher.hexdigest(), 16) % n
print("c:", c)
c_ = (c - delta) % n
print("c_:", c_)
s_ = (1 - c_ * d) % n
print("s_:", s_)
print("sign:", int.from_bytes(signer.sign(c_.to_bytes(32, 'big'), pv_key), 'big') % n)
s = (s_ + gama) % n
print("s:", s)
print((c * P + s * G))
print(t == (c * P + s * G).x % n)