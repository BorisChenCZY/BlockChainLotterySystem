from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey,ECPublicKey
from ecpy.eddsa import EDDSA
import hashlib
import settings
def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')
def init_key():
    cv = Curve.get_curve('secp256k1')
    pv_key = ECPrivateKey(int(hashlib.md5(settings.PRIVATE_KEY.encode()).hexdigest(), 16), cv)
    settings.PUBLIC_KEY = hex(int.from_bytes(cv.encode_point(pv_key.get_public_key().W),"big"))
    print(settings.PUBLIC_KEY)

if __name__ == "__main__":
    try:
        init_key()
    finally:
        pass
