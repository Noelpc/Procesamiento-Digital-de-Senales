#!/usr/bin/env python3
"""Pregunta 2 - Filtrado en frecuencia vs. filtrado en el tiempo."""
import numpy as np
import matplotlib.pyplot as plt
from common import savefig, save_json

h = np.float64([-0.98795743, -0.41598237, 0.18987709, 0.17960631, 0.03910364])
x = np.float64([0.96190914, 0.0778549, -0.123788, 0.15311194, -0.76289329,
                0.45288221, 0.08247743, -0.70759318, 0.15893536, -0.58270816])

# 2.A) convolución lineal en el tiempo
y_n = np.convolve(x, h)
L = len(x) + len(h) - 1                      # largo de la convolución lineal = 14

# 2.B/2.C) filtrado en frecuencia: NFFT potencia de 2 y NFFT >= L
NFFT = 1 << (L - 1).bit_length()             # 16
X = np.fft.fft(x, NFFT)                      # fft(x, NFFT) rellena con ceros hasta NFFT
H = np.fft.fft(h, NFFT)                      # h también, al mismo largo
Y = H * X                                    # producto punto a punto
y_full = np.fft.ifft(Y).real                 # IFFT (la parte imaginaria es ruido numérico)
y_w = y_full[:L]                             # descartar los NFFT-L ceros sobrantes

# contraejemplo: sin zero-padding suficiente (NFFT = 10) -> convolución circular
y_circ = np.fft.ifft(np.fft.fft(x, 10) * np.fft.fft(h, 10)).real

# 2.D) comparación
err = np.max(np.abs(y_n - y_w))
print("L =", L, " NFFT =", NFFT)
print("y_n =", np.round(y_n, 6))
print("y_w =", np.round(y_w, 6))
print("max|y_n - y_w| =", err, " allclose:", np.allclose(y_n, y_w))
print("sin padding (NFFT=10):", np.round(y_circ, 6), " max err vs y_n[:10] =", np.max(np.abs(y_circ - y_n[:10])))
print("residuo imaginario máx:", np.max(np.abs(np.fft.ifft(Y).imag)))

fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
ax[0].stem(np.arange(L), y_n, linefmt="#1f4e9c", markerfmt="o", basefmt=" ", label="y_n (convolución)")
ax[0].plot(np.arange(L), y_w, "x", color="#e09f00", ms=8, label="y_ω (IFFT{H·X})")
ax[0].set_title("Filtrado en tiempo vs. frecuencia (NFFT = 16)"); ax[0].legend(fontsize=7)
ax[0].set_xlabel("n")
ax[1].stem(np.arange(10), y_circ, linefmt="#2a9d8f", markerfmt="s", basefmt=" ", label="NFFT = 10 (circular)")
ax[1].plot(np.arange(10), y_n[:10], "o", mfc="none", color="#1f4e9c", label="y_n[0:10]")
ax[1].set_title("Sin zero-padding: aliasing temporal"); ax[1].legend(fontsize=7)
ax[1].set_xlabel("n")
savefig("p2_comparacion.png")

save_json("p2.json", dict(L=L, NFFT=NFFT, y_n=y_n, y_w=y_w, y_circ=y_circ, err=err))
