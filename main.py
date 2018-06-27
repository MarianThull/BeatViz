# coding=utf-8
__author__ = 'Dev'

from AudioStream import AudioStream
from SpectrumAnalyzer import SpectrumAnalyzer
from AsciiVizArt import AsciiVizArt
from PlotVizArt import PlotVizArt
import threading
import signal
import sys


class Main:
    def __init__(self):
        samplerate = 44100

        bins = 30
        fft_width = 8192
        min_f = 50
        max_f = 12000

        audio_buffer_size = 10240
        audio_chunk_size = 512

        analyzer_update_freq = 60
        visualizer_update_freq = 60

        vis_max_unfiltered_freq = 3
        filter_size = int(0.8 * visualizer_update_freq / vis_max_unfiltered_freq)

        self.stream = AudioStream(max(audio_buffer_size, fft_width), audio_chunk_size, samplerate)
        self.stream_thread = threading.Thread(target=self.stream.loop)
        self.stream_thread.start()

        self.analyzer = SpectrumAnalyzer(fft_width, samplerate, bins, self.stream,
                                         analyzer_update_freq, band_normalization_exp=0,
                                         min_f=min_f, max_f=max_f)
        self.analyzer_thread = threading.Thread(target=self.analyzer.loop)
        self.analyzer_thread.start()

        # self.visualizer = AsciiVizArt(self.analyzer, 5)
        # self.visualizer_thread = threading.Thread(target=self.visualizer.loop)
        # self.visualizer_thread.start()

        self.visualizer = PlotVizArt(self.analyzer, bins, filter_size, visualizer_update_freq, linear=True)
        self.visualizer_thread = threading.Thread(target=self.visualizer.loop)
        self.visualizer_thread.start()

    def shutdown(self):
        self.visualizer.close()
        self.stream.close()
        self.analyzer.close()
        self.visualizer_thread.join()
        self.stream_thread.join()
        self.analyzer_thread.join()
        print("Shutdown successful")


if __name__ == "__main__":
    m = Main()
    _ = input("Press enter to close...")
    m.shutdown()
