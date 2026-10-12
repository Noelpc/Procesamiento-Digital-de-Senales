#!/usr/bin/env python3
"""Problema 2: Oido de Elefante.

Una cancion enmascarada por ruido blanco gaussiano. Se usa unicamente la DFT:
  1) DFT de toda la senal: el ruido blanco da un piso plano; los tonos, picos.
  2) DFT por segmentos (ventana deslizante): nota dominante en funcion del tiempo.
Genera figuras/p2_cancion.png y muestra la secuencia de notas.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram

BASE = Path(__file__).resolve().parent
FIG = BASE / "figuras"
FIG.mkdir(exist_ok=True)

fs, s = wavfile.read(BASE / "senal_misteriosa.wav")
s = s.astype(float)
if s.ndim > 1:
    s = s.mean(axis=1)
s -= s.mean()
N = len(s)
print(f"fs = {fs} Hz, N = {N} muestras, duracion = {N / fs:.2f} s")

# 1) DFT global
S = np.abs(np.fft.rfft(s)) ** 2 / N
f = np.fft.rfftfreq(N, 1 / fs)
piso = np.median(S)
print(f"pico maximo / piso de ruido = {10 * np.log10(S.max() / piso):.1f} dB")

# 2) DFT por segmentos de 250 ms
nps = 4000
fx, tt, Sx = spectrogram(s, fs, nperseg=nps, noverlap=nps - 800, nfft=16384)
banda = (fx > 200) & (fx < 600)
NOMBRES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def nota(frec):
    m = int(round(69 + 12 * np.log2(frec / 440)))       # numero MIDI
    return NOMBRES[m % 12] + str(m // 12 - 1)


seq = [nota(fx[banda][np.argmax(Sx[banda, i])]) for i in range(len(tt))]
tramos = []                                               # (nota, t_ini, t_fin)
for i, n in enumerate(seq):
    if tramos and tramos[-1][0] == n:
        tramos[-1][2] = tt[i]
    else:
        tramos.append([n, tt[i], tt[i]])
tramos = [q for q in tramos if q[2] - q[1] > 0.1]

print("\nNota   t_ini [s]  t_fin [s]")
for n, a, b in tramos:
    print(f"{n:<6} {a:8.2f}  {b:8.2f}")
print("\nSecuencia:", " ".join(q[0] for q in tramos))
print("Conclusion: la melodia corresponde al 'Himno a la Alegria' (Beethoven, Sinfonia n.o 9).")

fig, ax = plt.subplots(2, 1, figsize=(7.2, 5.6))
ax[0].semilogy(f, S, lw=0.4); ax[0].set_xlim(0, 1000)
ax[0].axhline(piso, color="r", ls="--", lw=0.8, label="piso de ruido (mediana)")
ax[0].set_xlabel("f [Hz]"); ax[0].set_ylabel("|X[k]|^2 / N")
ax[0].set_title("Periodograma de toda la senal"); ax[0].legend(); ax[0].grid(alpha=0.3)
ax[1].pcolormesh(tt, fx[fx < 600], 10 * np.log10(Sx[fx < 600]), shading="auto")
ax[1].set_ylim(200, 500); ax[1].set_xlabel("t [s]"); ax[1].set_ylabel("f [Hz]")
ax[1].set_title("Espectrograma (ventana 250 ms)")
for n, a, b in tramos:
    ax[1].text((a + b) / 2, 480, n, color="w", fontsize=6, ha="center")
plt.tight_layout(); plt.savefig(FIG / "p2_cancion.png", dpi=170); plt.close()
