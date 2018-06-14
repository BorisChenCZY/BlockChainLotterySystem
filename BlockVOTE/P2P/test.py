import datetime
import asyncio
import time
if __name__ == "__main__":
    now = datetime.datetime.timestamp(datetime.datetime.now())
    time.sleep(1)
    xixi = datetime.datetime.timestamp(datetime.datetime.now())
    diff = (datetime.datetime.fromtimestamp(xixi) - datetime.datetime.fromtimestamp(now))
    print(type(diff.seconds))
    # print(type(diff))