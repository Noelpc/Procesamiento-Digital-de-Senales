#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from random import uniform

A = np.float64([[uniform(0.1, 2) for _ in range(5)] for _ in range(5)])
P = np.float64([[uniform(0, 2*np.pi) for _ in range(5)] for _ in range(5)])
F = np.float64([100, 200, 300, 400, 500])
Fs = 22050
f = F/Fs
cycles = 10
N = int(Fs//F[0])*cycles
n = np.arange(N)

w = signal.windows.hamming(N)

x = np.zeros((N,5))

for i in range(5):
    for j in range(5):
        x[:,i] += A[j][i]*np.cos(2*np.pi*f[j]*n + P[j][i])
    x[:,i] *= w

plt.plot (x)
plt.show()

# Las señales a utilizar
x1 = x[:,0]
x2 = x[:,1]
x3 = x[:,2]
x4 = x[:,3]
x5 = x[:,4]
