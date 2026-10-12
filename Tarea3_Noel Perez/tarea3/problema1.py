#!/usr/bin/env python3
"""Problema 1: Hacker de Sonar.

a) Operador: correlacion cruzada  r_yx[k] = sum_n y[n] x[n-k]
b) Chirp lineal construido desde su expresion matematica
c) Retardo y distancia con sonar_channel()
d) Resolucion espacial
e) Duracion minima y maxima del chirp (ecuacion de SONAR activo)

Genera las figuras en figuras/ y muestra los resultados por consola.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # sin ventana: funciona en servidores
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import correlate, correlation_lags

from sonar_channel import sonar_channel

FIG = Path(__file__).resolve().parent / "figuras"
FIG.mkdir(exist_ok=True)

# ---------------- Parametros ----------------
fi, ff, T, fs = 20e3, 30e3, 10e-3, 96e3     # Hz, Hz, s, Hz
c = 1500.0                                   # m/s, velocidad del sonido en agua salada (supuesto)

# ---------------- b) Chirp lineal ----------------
# x(t) = cos[2*pi*(fi*t + (ff-fi)/(2T) * t^2)],  0 <= t < T
t = np.arange(int(round(T * fs))) / fs
x = np.cos(2 * np.pi * (fi * t + (ff - fi) / (2 * T) * t**2))

plt.figure(figsize=(7, 3))
plt.plot(t * 1e3, x, lw=0.6)
plt.xlabel("t [ms]"); plt.ylabel("x(t)")
plt.title("Chirp lineal 20-30 kHz, T = 10 ms, fs = 96 kHz")
plt.grid(alpha=0.3); plt.tight_layout()
plt.savefig(FIG / "p1_chirp.png", dpi=170); plt.close()

# ---------------- c) Retardo y distancia ----------------
y = sonar_channel(x, fs)
r = correlate(y, x, mode="full", method="fft")           # r_yx[k]
lags = correlation_lags(len(y), len(x), mode="full")
causal = lags >= 0                                        # solo retardos fisicamente validos
k = lags[causal][np.argmax(r[causal])]                    # indice del maximo
tau = k / fs                                              # retardo [s]
R = c * tau / 2                                           # distancia [m] (ida y vuelta)

resto = np.delete(np.abs(r[causal]), np.arange(max(0, k - 20), k + 20))
print("=== Inciso c ===")
print(f"muestras: x = {len(x)}, y = {len(y)}")
print(f"k = {k} muestras -> tau = {tau * 1e3:.3f} ms")
print(f"R = c*tau/2 = {c:.0f} * {tau:.4f} / 2 = {R:.2f} m")
print(f"pico / std(resto) = {np.abs(r[causal])[k] / resto.std():.1f}")

plt.figure(figsize=(7, 3))
plt.plot(lags[causal] / fs * 1e3, r[causal], lw=0.6)
plt.axvline(tau * 1e3, color="r", ls="--", label=f"pico: tau = {tau * 1e3:.1f} ms")
plt.xlabel("retardo [ms]"); plt.ylabel("r_yx[k]")
plt.title("Correlacion cruzada entre recibida y transmitida")
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
plt.savefig(FIG / "p1_correlacion.png", dpi=170); plt.close()

# ---------------- d) Resolucion espacial ----------------
B = ff - fi
dR = c / (2 * B)
print("\n=== Inciso d ===")
print(f"B = {B / 1e3:.1f} kHz -> dR = c/(2B) = {dR * 100:.1f} cm")

# ---------------- e) Duracion minima y maxima ----------------
SL, DI, TS = 190.0, 10.0, -5.0               # dB
NL0, alpha, SNR_min = 69.2, 6.0, 10.0        # dB, dB/km, dB
TL = 20 * np.log10(R) + alpha * (R / 1000)   # perdida de transmision [dB]
NL = NL0 + 10 * np.log10(B)                  # ruido en la banda [dB]
# SNR = SL - 2TL + TS - NL + DI + 10 log10(B T) >= SNR_min
PG_min = SNR_min - (SL - 2 * TL + TS - NL + DI)
T_min = 10 ** (PG_min / 10) / B
T_max = 2 * R / c                            # el eco no debe solaparse con la transmision

print("\n=== Inciso e ===")
print(f"TL = {TL:.2f} dB, 2TL = {2 * TL:.2f} dB, NL = {NL:.2f} dB")
print(f"SNR(T) = {SL - 2 * TL + TS - NL + DI + 10 * np.log10(B):.2f} + 10 log10(T) dB")
print(f"PG minima = {PG_min:.2f} dB")
print(f"T_min = {T_min * 1e3:.2f} ms")
print(f"T_max = 2R/c = {T_max * 1e3:.1f} ms")
print(f"T usado = {T * 1e3:.0f} ms -> cumple: {T_min <= T <= T_max}")
