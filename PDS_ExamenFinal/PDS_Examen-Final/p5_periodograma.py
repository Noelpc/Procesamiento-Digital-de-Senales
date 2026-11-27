#!/usr/bin/env python3
"""Pregunta 5 - Periodograma vs. estimador de Welch (crowd.wav)."""
import os
import numpy as np
import scipy.signal as sg
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from common import savefig, save_json, DATA

fs, x = wavfile.read(os.path.join(DATA, "crowd.wav"))
x = x.astype(np.float64) / 32768.0
x -= x.mean()                                           # quitar DC (media estimada)
N = len(x)

# 5.C-1 periodograma clásico: P(f) = |X(f)|^2 / (N fs)  (rectangular, N puntos)
f_per, P_per = sg.periodogram(x, fs=fs, window="boxcar", detrend=False, scaling="density")
dB = lambda p: 10 * np.log10(p + 1e-20)

# 5.C-2 Welch: segmentos de L muestras, 50 % de traslape, ventana Hann
L = 2048
noverlap = L // 2
f_w, P_w = sg.welch(x, fs=fs, window="hann", nperseg=L, noverlap=noverlap, detrend=False, scaling="density")
step = L - noverlap
K = (N - noverlap) // step                                # nº de segmentos promediados
rho = 1 / 6                                               # correlación entre segmentos Hann 50 %
K_eff = K / (1 + 2 * rho ** 2)
var_ratio = 1 / K_eff
print(f"N={N} fs={fs} L={L} K={K} K_eff={K_eff:.1f} var_ratio≈{var_ratio:.4f} ({10*np.log10(var_ratio):.1f} dB)")

# verificación empírica con ruido blanco gaussiano de la misma longitud (PSD plana conocida)
rng = np.random.default_rng(0)
vr = []
for _ in range(20):
    wn = rng.standard_normal(N)
    _, pp = sg.periodogram(wn, window="boxcar", detrend=False)
    _, pw = sg.welch(wn, window="hann", nperseg=L, noverlap=noverlap, detrend=False)
    vr.append(np.var(pw[5:-5]) / np.mean(pw[5:-5]) ** 2 / (np.var(pp[5:-5]) / np.mean(pp[5:-5]) ** 2))
vr_emp = float(np.mean(vr))
print(f"razón de varianzas empírica (ruido blanco) = {vr_emp:.4f}")

# gráficos
fig, ax = plt.subplots(2, 1, figsize=(8.5, 7))
ax[0].plot(f_per, dB(P_per), lw=0.4, color="#9bb7d4", label=f"Periodograma (N = {N})")
ax[0].plot(f_w, dB(P_w), lw=1.4, color="#1f4e9c", label=f"Welch (L = {L}, Hann, 50 %, K = {K})")
ax[0].set_xlim(0, fs / 2); ax[0].set_ylim(-115, -35); ax[0].set_ylabel("PSD [dB/Hz]"); ax[0].set_xlabel("Frecuencia [Hz]")
ax[0].set_title("Periodograma original y mejorado (escala lineal en frecuencia)"); ax[0].legend(fontsize=8)
ax[1].semilogx(f_per[1:], dB(P_per[1:]), lw=0.4, color="#9bb7d4", label="Periodograma")
ax[1].semilogx(f_w[1:], dB(P_w[1:]), lw=1.4, color="#1f4e9c", label="Welch")
ax[1].set_xlim(20, fs / 2); ax[1].set_ylabel("PSD [dB/Hz]"); ax[1].set_xlabel("Frecuencia [Hz] (log)")
ax[1].set_title("Misma comparación en escala logarítmica de frecuencia"); ax[1].legend(fontsize=8)
savefig("p5_periodograma_welch.png")

# otros L para ilustrar compromiso resolución / varianza
plt.figure(figsize=(8.5, 3.6))
for Lx, col in zip((512, 2048, 8192), ("#2a9d8f", "#1f4e9c", "#6a3d9a")):
    fx, px = sg.welch(x, fs=fs, window="hann", nperseg=Lx, noverlap=Lx // 2, detrend=False)
    plt.semilogx(fx[1:], dB(px[1:]), lw=1.0, color=col, label=f"L = {Lx}")
plt.xlim(20, fs / 2); plt.xlabel("Frecuencia [Hz] (log)"); plt.ylabel("PSD [dB/Hz]"); plt.legend(fontsize=8)
plt.title("Efecto de la longitud de segmento L en Welch")
savefig("p5_welch_L.png")

# contenido espectral (para 5.E)
df = f_w[1] - f_w[0]
Pt = np.sum(P_w) * df
cum = np.cumsum(P_w) * df / Pt
f_pico = f_w[np.argmax(P_w[2:]) + 2]
q = {p: float(f_w[np.searchsorted(cum, p / 100)]) for p in (50, 80, 90, 95, 99)}
def banda(a, b): return float(np.sum(P_w[(f_w >= a) & (f_w < b)]) * df / Pt * 100)
bandas = {"0-100": banda(0, 100), "100-500": banda(100, 500), "500-1000": banda(500, 1000),
          "1000-2000": banda(1000, 2000), "2000-4000": banda(2000, 4000), "4000-5512": banda(4000, fs / 2 + 1)}
dBs = lambda f0: float(dB(P_w[np.argmin(np.abs(f_w - f0))]))
niveles = {str(f0): dBs(f0) for f0 in (100, 300, 1000, 2000, 4000, 5000)}
print("pico en", f_pico, "Hz; cuantiles de energía", q); print("bandas %", bandas); print("niveles dB", niveles)

save_json("p5.json", dict(fs=fs, N=N, L=L, K=K, K_eff=K_eff, var_ratio=var_ratio, var_db=10 * np.log10(var_ratio),
                          vr_emp=vr_emp, f_pico=float(f_pico), cuantiles=q, bandas=bandas, niveles=niveles,
                          res_per=fs / N, res_welch=fs / L * 1.5))
