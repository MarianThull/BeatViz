# coding=utf-8
__author__ = 'Dev'

from LoopedThread import LoopedThread
import os
import numpy as np


class AsciiVizArt(LoopedThread):
    def __init__(self, analyzer, update_freq):
        LoopedThread.__init__(self, update_freq)
        self.analyzer = analyzer

        self.max_dB = 0
        self.min_dB = -80
        self.levels = 16

    def main(self):
        spectrum = self.analyzer.get_spectrum()
        log_spectrum = list(map(lambda x: self.min_dB if x == 0 else 20 * np.log10(x), spectrum))

        # os.system("cls")
        print()
        for bin in log_spectrum[::-1]:
            level = max(int((-self.min_dB + bin) / (-self.min_dB / self.levels)), 0)
            print("_" * level)
        print("", flush=True)
