from aiohttp import web

def vote_receiver():
    __sio = socketio.AsyncServer()
    app = web.Application()
    __sio.attach(app)

    @__sio.on('connect')
    def connect(sid, environ):
        print('connect', sid)

    @__sio.on("Vote")
    def vote(sid, data):
        d = json.loads(data)
        # 对接收到的信息中的投票平台公钥是否在自己公钥池中，在就直接解密，然后得到用户投票信息和用户公钥；
        data = d["data"]
        sig = d["sign"]
        key_info = data['pubkey']
        target = data['target']
        prob_num = data['prob_num']
        selection = data['selection']

        key_info = key_info.encode("utf-8")

        vote = "{}:{}".format(data['prob_num'], data['selection'])

        voteInfo = VoteInfo(get_timestamp(), target=target.encode("utf-8"), pubkey=key_info,
                            vote=(prob_num, selection), sign=sig.encode("utf-8"))
        # print(voteInfo)
        __chain.add_vote(voteInfo, -1)
        __cnt += 1
        if __cnt >= 5:
            __cnt = 0
            pack_block()
        block_recv(BQUEUE)
        return "OK", 123

    web.run_app(app, port=addr[1])