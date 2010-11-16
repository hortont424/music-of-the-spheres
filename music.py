from pyaudio import PyAudio, paInt32
from struct import pack
from math import sin, pi

p = PyAudio()

sampleRate = 44100

stream = p.open(format = paInt32,
                channels = 1,
                rate = sampleRate,
                output = True,
                frames_per_buffer = 1)

oscillators = [lambda t: (100 + sin(t) * 10, 819200000), lambda t: (103, 819200000)]

for i in range(0, sampleRate * 25):
    seconds = float(i) / sampleRate
    oscvals = [osc(seconds) for osc in oscillators]
    sample = sum([(sin(seconds * a * 2 * pi) * b) for a, b in oscvals])
    stream.write(pack("i", sample), 1)

stream.stop_stream()
stream.close()
p.terminate()