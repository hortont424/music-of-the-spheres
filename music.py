import sys

from pyaudio import PyAudio, paInt32
from struct import pack
from math import sin, pi, sqrt

p = PyAudio()

sampleRate = 44100
framesPerBuffer = 4096

stream = p.open(format = paInt32,
                channels = 1,
                rate = sampleRate,
                output = True,
                frames_per_buffer = framesPerBuffer)

class Body(object):
    def __init__(self, x, y, z, f):
        super(Body, self).__init__()
        self.pos = (x, y, z)
        self.f = f

    def distance(self, pos):
        return sqrt(sum([(a - b) ** 2 for (a, b) in zip(self.pos, pos)]))

class Particle(object):
    def __init__(self):
        self.pos = (0, 0, 0)
        self.v = (0, 0, 0)
        self.a = (0, 0, 0)

    def updatePosition(self):
        f = [10 / (body.distance(self.pos) ** 2) for body in bodies]

mainParticle = Particle()
bodies = [Body(10, 10, 10, 220), Body(5, -5, 3, 440), Body(-15, -10, -10, 330), Body(5, 5, 3, 550)]
oscillators = [(lambda t, body=body: (body.f, 0.5 / (body.distance(mainParticle.pos) ** 2))) for body in bodies]

for i in range(0, sampleRate * 25, framesPerBuffer):
    data = []
    for j in range(i, i + framesPerBuffer):
        seconds = float(j) / sampleRate
        oscvals = [osc(seconds) for osc in oscillators]
        sample = sum([(sin(seconds * a * 2 * pi) * ((2 ** 31 - 2) * b)) for a, b in oscvals])
        data.append(sample)
        mainParticle.updatePosition()

    stream.write(pack("{0}i".format(framesPerBuffer), *data), framesPerBuffer)

stream.stop_stream()
stream.close()
p.terminate()