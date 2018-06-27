# coding=utf-8
__author__ = 'Dev'

import time


class LoopedThread:
    def __init__(self, update_freq=0):
        self.CLOSE = False
        self.wait_time = 1 / update_freq if update_freq else 0

    def loop(self):
        while not self.CLOSE:
            self.main()
            time.sleep(self.wait_time)
        self.finalize()

    def close(self):
        self.CLOSE = True

    def main(self):
        pass
        # override

    def finalize(self):
        pass
