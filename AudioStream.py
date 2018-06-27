# coding=utf-8
__author__ = 'Dev'


import numpy as np
import pyaudio
import sys
from LoopedThread import LoopedThread


class RingBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = np.zeros(size, dtype=np.int)
        self.pointer = 0  # next index to write

    def __repr__(self):
        s = " " + "  " * self.pointer + "|\n"
        return s + str(self.buffer)

    def write(self, data):
        data_length = len(data)
        overhead = self.pointer + data_length - self.size
        if overhead > 0:
            self.buffer[0:overhead] = data[data_length - overhead:]
            data = data[:data_length - overhead]
        self.buffer[self.pointer:self.pointer + len(data)] = data
        self.pointer = (self.pointer + data_length) % self.size

    def write_single(self, int_data):
        self.buffer[self.pointer] = int_data
        self.pointer = (self.pointer + 1) % self.size

    def read(self, length):
        data = np.zeros(length, dtype=np.int)
        start_index = self.pointer - length
        underhead = 0
        if start_index < 0:
            underhead = abs(start_index)
            data[0:underhead] = self.buffer[start_index:]
            start_index = 0
        data[underhead:] = self.buffer[start_index:start_index + length - underhead]
        return data


class AudioStream(LoopedThread):
    def __init__(self, buffersize, chunk, samplerate):
        LoopedThread.__init__(self)
        self.chunk = chunk
        self.buffer = RingBuffer(buffersize)
        self.p = pyaudio.PyAudio()

        stereomix_index = -1
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(str(i) + '. ' + dev['name'])
                if dev['name'].lower().startswith("stereomix"):
                    stereomix_index = i
        print("Stereomix index: " + str(stereomix_index))

        if stereomix_index < 0:
            print("FATAL ERROR: HAAAAALPPP!!!")
            sys.exit(1)

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=samplerate,
                                  input=True,
                                  frames_per_buffer=chunk,
                                  input_device_index=stereomix_index)
        print("Opened stereomix input stream.")

    def main(self):
        data = self.stream.read(self.chunk)
        for i in range(int(len(data) / 2)):
            self.buffer.write_single(int.from_bytes(data[i * 2: (i + 1) * 2],
                                                    "little", signed=True))
        # print(self.read(16))

    def finalize(self):
        print("Stream stopping")
        self.stream.close()
        self.p.terminate()

    def read(self, size):
        return self.buffer.read(size)


if __name__ == "__main__":
    a = AudioStream(1024, 512)
    a.loop()
