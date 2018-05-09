import re
import datetime
import time


class VoteInfoError(Exception):
    pass


class VoteInfo():
    __target = None
    __timestamp = None
    __pubkey = None
    __sign = None
    __info = None
    __prob_id = None
    __selections = None

    def __init__(self, timestamp=None, target=None, pubkey=None, vote=None, sign = None):
        if (timestamp):
            self.set_timestamp(timestamp)
        if (target):
            self.set_target(target)
        if (pubkey):
            self.set_pubkey(pubkey)
        if (vote):
            self.set__info(vote)
        if (sign):
            self.set_sign(sign)

    def set_target(self, target):
        if (type(target) != bytes):
            raise VoteInfoError("target type must be bytes")
        self.__target = target

    def get_target(self):
        return self.__target

    def set_timestamp(self, timestamp):
        if (type(timestamp) != float):
            raise VoteInfoError("timestamp must be float")
        self.__timestamp = bytes(str(timestamp).encode('utf-8'))

    def get_timestamp(self):
        return self.__timestamp

    def set_pubkey(self, pubkey):
        if (type(pubkey) != bytes):
            raise VoteInfoError("pubkey type must by bytes")
        self.__pubkey = pubkey

    def get_pubkey(self):
        return self.__pubkey

    def set_sign(self, sign):
        if (type(sign) != bytes):
            raise VoteInfoError("sign must be bytes")
        self.__sign = sign

    def get_sign(self):
        return self.__sign

    def set__info(self, vote):
        """
        :tuple(int, (list of) int): vote[0] represents question_id, vote[1] represents the selection of that question_id,
                                    it accepts an int or a list of ints
        :return: None
        """
        if (type(vote[0]) != int):
            raise VoteInfoError("The first element of vote(vote[0]) must be int.")
        if (type(vote[1]) != int and type(vote[1]) != list):
            raise VoteInfoError("The second element of vote(vote[1]) must by int or list of int")
        self.__prob_id = vote[0]
        self.__selections = vote[1]
        sel = "[{}:".format(vote[0])
        selects = vote[1]
        if type(selects) == list:
            for op in selects:
                if (type(op) != int):
                    raise VoteInfoError("elements inside votes[1] must be int")
                sel += str(op) + ","
            sel = sel[:-1]
        else:
            sel += selects

        sel += "]"
        self.__info = bytes(sel.encode("utf-8"))

    def get_info(self):
        return self.__info

    def get_prob_id(self):
        return self.__prob_id

    def get_selection(self):
        return self.__selections

    def check(self):
        # todo
        return True

    def __bytes__(self):
        if (not self.__timestamp):
            raise VoteInfoError("timestamp not set yet")
        if (not self.__info):
            raise VoteInfoError("vote information not set yet")
        if (not self.__pubkey):
            raise VoteInfoError("pubkey not set yet")
        if (not self.__target):
            raise VoteInfoError("target not set yet")
        if (not self.__sign):
            raise VoteInfoError("sign not set yet")
        s = "{timestamp}|{target}|{pubkey}|{info}".format(timestamp=self.__timestamp
                                                          , target=self.__target
                                                          , pubkey=self.__pubkey
                                                          , info=self.__info)
        return self.__timestamp + b"|" + \
               self.__target + b"|" + \
               self.__pubkey + b"|" + \
               self.__info + b"|" + \
               self.__sign + b"|"

    @staticmethod
    def load(vote):
        components = vote.split(b"|")
        timestamp = float(components[0])
        target = components[1]
        pubkey = components[2]
        vote_str = components[3].decode("utf-8")
        sign = components[4]
        quesid, selections = VoteInfo.parse_info(vote_str)
        return VoteInfo(timestamp, target, pubkey, (quesid, selections), sign)

    @staticmethod
    def parse_info(vote_str):
        quesid = int(re.findall(r"([0-9]+)", vote_str.split(":")[0])[0])
        selections_str = vote_str.split(":")[1]
        selections = []
        for sel in selections_str.split(","):
            if(sel.strip() == ""):
                continue
            selections.append(int(re.findall(r"[0-9]+", sel)[0]))
        return quesid, selections


if __name__ == "__main__":
    # timestamp = datetime.datetime.now().timestamp()  # current time
    # pubkey = b'pubkey'
    # target = b'target'
    # vote = (1, [1, 2, 3])
    # voteInfo = VoteInfo(timestamp=timestamp, target=target, pubkey=pubkey, vote=vote)
    # print(bytes(voteInfo))
    print(VoteInfo.parse_info("[1:1]"))
