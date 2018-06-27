# coding=utf-8
__author__ = 'Dev'

from LoopedThread import LoopedThread

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation


class PlotVizArt(LoopedThread):
    def __init__(self, analyzer, bins, filter_size, update_freq, linear=False):
        LoopedThread.__init__(self, 0.5)
        self.analyzer = analyzer
        self.min_dB = -80
        self.bins = bins
        self.filter_size = filter_size

        self.register = []
        self.init_register()
        self.weights = self.calc_weights() if not linear else self.calc_weights_lin()

        self.line = None
        self.start_animation(update_freq)

    def calc_weights_lin(self):
        return np.zeros(self.filter_size) + (1 / self.filter_size)

    def calc_weights(self):
        weights = np.zeros(self.filter_size)
        for i in range(self.filter_size):
            weights[i] = (0.54 - 0.46 * np.cos(2 * np.pi * i / self.filter_size)) *\
                         (0.1 * np.sinc((i - self.filter_size / 2) / 10))

        return weights

    def init_register(self):
        for _ in range(self.filter_size):
            self.register.append(np.zeros(self.bins) - 80.0)

    def start_animation(self, update_freq):
        fig, ax = plt.subplots()
        ax.set_xlim(-1, self.bins)
        ax.set_ylim(-100.0, 10.0)

        x_vals = np.arange(0, self.bins, 1)
        self.line, = ax.plot(x_vals, np.zeros(self.bins, dtype=np.float64),
                             linewidth=0, marker='_', markersize=12, color="red")

        a = animation.FuncAnimation(fig, self.animate, 100, interval=int(1 / update_freq),
                                    repeat=True, blit=True, init_func=self.init)
        plt.show()

    def init(self):
        self.line.set_ydata(np.zeros(self.bins, dtype=np.float64))
        return self.line,

    def animate(self, _i):
        spectrum = self.analyzer.get_spectrum()
        y_vals = np.array(
            list(map(lambda x: self.min_dB if x == 0 else max(20 * np.log10(x), self.min_dB), spectrum)),
            dtype=np.float64)

        self.register.insert(0, y_vals)
        self.register.pop(-1)

        output = np.zeros(self.bins)
        for i in range(self.filter_size):
            output += self.register[i] * self.weights[i]

        self.line.set_ydata(output)
        return self.line,

    def main(self):
        pass
