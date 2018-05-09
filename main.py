from RSA import *

if __name__ == '__main__':
    # generate public & private key
    pubkey, privkey = get_keys()
    # save public key
    save(pubkey, "./pub.pem")
    save(privkey, "./priv.pem")
    # load public key
    pubkey = load("./pub.pem", 0)
    privkey = load("./priv.pem", 1)
    # sign message
    message = "hello world".encode("utf-8")
    sig = sign(message, privkey)
    # verify sign
    is_true = verify(message, sig, pubkey)
    print(is_true)