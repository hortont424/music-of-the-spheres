import wave

from struct import pack, calcsize
from math import sin, pi, sqrt
from random import randint, gauss
from progressbar import ProgressBar, Bar, ETA

sampleRate = 44100
framesPerStep = 128
duration = 10
worldScale = 30
bodyCount = 5
freqScale = (50, 2000)
G = 0.001

class Body(object):
    def __init__(self, x, y, z, m, f):
        super(Body, self).__init__()
        self.pos = (x, y, z)
        self.m = m
        self.f = f

    def distance(self, pos):
        return sqrt(sum([(a - b) ** 2 for (a, b) in zip(self.pos, pos)])) + 0.1 # LOLOLOLOL

class Particle(object):
    def __init__(self):
        self.pos = (0, 0, 0)
        self.v = (0, 0, 0)
        self.a = (0, 0, 0)

    def updatePosition(self):
        self.a = (0, 0, 0)
        for body in bodies:
            direction = [a - b for a, b in zip(self.pos, body.pos)]
            directionMagnitude = sqrt(sum([a ** 2 for a in direction]))
            direction = [a / directionMagnitude for a in direction]
            accel = (-G * body.m) / (body.distance(self.pos) ** 2)
            self.a = (self.a[0] + accel * direction[0], self.a[1] + accel * direction[1], self.a[2] + accel * direction[2])

        self.v = [sum(v) for v in zip(self.a, self.v)]
        self.pos = [sum(v) for v in zip(self.v, self.pos)]

mainParticle = Particle()

bodies = []
for i in range(bodyCount):
    bodies.append(Body(randint(-worldScale, worldScale),
                       randint(-worldScale, worldScale),
                       randint(-worldScale, worldScale),
                       10 * gauss(1, 0.2),
                       randint(*freqScale)))

oscillators = [(lambda t, body=body: (body.f, 0.5 / body.distance(mainParticle.pos) ** 2)) for body in bodies]

outputData = []

data = [0] * framesPerStep

progress = ProgressBar(widgets=[Bar(), " ", ETA()], maxval = sampleRate * duration)

for i in range(0, sampleRate * duration, framesPerStep):
    for j in range(i, i + framesPerStep):
        seconds = float(j) / sampleRate
        oscvals = [osc(seconds) for osc in oscillators]
        sample = sum([(sin(seconds * a * 2 * pi) * ((2 ** 31 - 2) * b)) for a, b in oscvals])

        if sample > (2 ** 31) * 0.7:
            sample = (2 ** 31) * 0.7
            print "volume limit exceeded"

        if sample < 0:
            sample = 0

        data[j - i] = sample

    mainParticle.updatePosition()
    progress.update(i)

    outputData.append(pack("{0}i".format(framesPerStep), *data))

outputData = ''.join(outputData)
wf = wave.open("out.wav", 'wb')
wf.setnchannels(1)
wf.setsampwidth(calcsize("i"))
wf.setframerate(sampleRate)
wf.writeframes(outputData)
wf.close()