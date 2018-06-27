# coding=utf-8
__author__ = 'Dev'

import numpy as np
import time
from LoopedThread import LoopedThread


class SpectrumAnalyzer(LoopedThread):
    def __init__(self, samplesize, samplerate, no_bands, stream,
                 update_freq, band_normalization_exp=0, min_f=20, max_f=20000):
        LoopedThread.__init__(self, update_freq)
        self.samplesize = samplesize
        self.samplerate = samplerate
        self.stream = stream
        self.bands = None
        self.band_power = np.zeros(no_bands, float)
        self.power = 0
        self.calculate_output_bands(min_f, max_f, no_bands)
        self.update_freq = update_freq
        self.band_normalization_exp = band_normalization_exp

    def calculate_output_bands(self, min_f, max_f, no_bands):
        self.bands = np.logspace(np.log10(min_f), np.log10(max_f), no_bands + 1)

    # def calc_constQ_kernel(self, freq_min, freq_max, bins, thresh):
    #     Q = 1 / (2 ** (1 / bins) - 1)
    #     K = np.ceil(bins * np.log2(freq_max / freq_min))
    #     fft_len = self.next_pow2(np.ceil(Q * self.samplerate / freq_min))
    #     temp_kernel = np.zeros(fft_len)
    #     sparse_kernel = np.
    #
    # @staticmethod
    # def next_pow2(x):
    #     i = 0
    #     while True:
    #         if x <= 2 ** i:
    #             return 2 ** i
    #         i += 1

    def fft(self):
        sample = self.stream.read(self.samplesize)
        normed_sample = (1 / 2**15) * sample.astype(float)
        windowed = self.window_function(normed_sample)
        full_spectrum = np.abs((1 / self.samplesize) * np.fft.fft(windowed))

        power = self.rms(full_spectrum)
        band_power = np.zeros(len(self.bands) - 1, float)

        freq_step = self.samplerate / self.samplesize
        for band in range(len(self.bands) - 1):
            freq_low = self.bands[band]
            freq_high = self.bands[band + 1]
            amp_index_low = int(np.ceil(freq_low / freq_step))
            amp_index_high = int(np.floor(freq_high / freq_step))
            bin_size = amp_index_high - amp_index_low
            # print(bin_size)
            if bin_size:
                band_power[band] = self.rms(full_spectrum[amp_index_low:amp_index_high + 1] /
                                            (bin_size ** self.band_normalization_exp))
            else:
                band_power[band] = 0

        return band_power, power

    @staticmethod
    def rms(fragment):
        return np.sqrt(sum(map(lambda x: x ** 2, fragment)))

    def main(self):
        self.band_power, self.power = self.fft()
        # print(list(map(lambda x: int(x * 1000) / 1000, band_power)))

    def window_function(self, sample):
        a0 = 1
        a1 = 1.93
        a2 = 1.29
        a3 = 0.388
        a4 = 0.028
        m = self.samplesize
        f = lambda n: a0 - a1 * np.cos(2*np.pi*n/(m-1))\
                      + a2 * np.cos(4*np.pi*n/(m-1))\
                      - a3 * np.cos(6*np.pi*n/(m-1))\
                      + a4 * np.cos(8*np.pi*n/(m-1))
        func_values = np.fromfunction(f, (self.samplesize,))

        return np.multiply(sample, func_values)

    def get_spectrum(self):
        return self.band_power

    def get_power(self):
        return self.power


if __name__ == "__main__":
    s = SpectrumAnalyzer(16, 44100, 10, None)
    s.window_function([])
