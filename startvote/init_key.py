from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey,ECPublicKey
from ecpy.eddsa import EDDSA
import hashlib
import settings

def init_key():
    cv = Curve.get_curve('Ed25519')
    pv_key = ECPrivateKey(int(hashlib.md5(settings.PRIVATE_KEY.encode()).hexdigest(), 16), cv)
    settings.PUBLIC_KEY = cv.encode_point(EDDSA.get_public_key(pv_key).W).hex()
