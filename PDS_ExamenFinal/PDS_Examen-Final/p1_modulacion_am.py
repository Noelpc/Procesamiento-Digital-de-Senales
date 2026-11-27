#!/usr/bin/env python3
"""Pregunta 1 - Modulación por amplitud (multiplexación por división de frecuencia).

Genera las 5 señales de pregunta1.py, las modula en 5 canales, las suma en una
única señal, las demodula con un FIR de fase lineal y verifica magnitud y fase.
"""
import random
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from common import savefig, save_json

# ---------------------------------------------------------------- señales (pregunta1.py)
random.seed(2026)                       # reproducible
uniform = random.uniform
A = np.float64([[uniform(0.1, 2) for _ in range(5)] for _ in range(5)])
P = np.float64([[uniform(0, 2 * np.pi) for _ in range(5)] for _ in range(5)])
F = np.float64([100, 200, 300, 400, 500])
Fs = 22050
f = F / Fs
cycles = 10
N = int(Fs // F[0]) * cycles
n = np.arange(N)
w = signal.windows.hamming(N)
x = np.zeros((N, 5))
for i in range(5):
    for j in range(5):
        x[:, i] += A[j][i] * np.cos(2 * np.pi * f[j] * n + P[j][i])
    x[:, i] *= w
t_ms = n / Fs * 1e3

# ---------------------------------------------------------------- 1.B / 1.C plan de canales
BW = 500.0                               # ancho de banda de cada señal [Hz]
fc = np.array([2000, 4000, 6000, 8000, 10000.0])   # portadoras [Hz]
tabla = [("Banda Base", None, 0.0, BW)] + [
    (f"Canal {k+1}", fc[k] - BW, fc[k], fc[k] + BW) for k in range(5)]

# ---------------------------------------------------------------- 1.E modulación
xm = np.zeros(N)
for k in range(5):
    xm += np.cos(2 * np.pi * fc[k] / Fs * n) * x[:, k]

plt.figure(figsize=(8, 3))
plt.plot(t_ms, xm, lw=0.7)
plt.xlabel("Tiempo [ms]"); plt.ylabel("Amplitud")
plt.title("Señal combinada x_m(n) = Σ cos(2π f_c n) x_k(n)")
savefig("p1_combinada_tiempo.png")

NFFT = 2 ** 15
fr = np.fft.rfftfreq(NFFT, 1 / Fs)
Xm = np.abs(np.fft.rfft(xm, NFFT)) / N
plt.figure(figsize=(8, 3.4))
plt.plot(fr, Xm, lw=0.8, color="#1f4e9c")
for k in range(5):
    plt.axvspan(fc[k] - BW, fc[k] + BW, color=["#2a9d8f", "#e09f00", "#6a3d9a", "#2e7d32", "#555555"][k], alpha=0.18)
    plt.text(fc[k], Xm.max() * 1.02, f"Canal {k+1}\n{fc[k]/1e3:.0f} kHz", ha="center", va="bottom", fontsize=7)
plt.xlim(0, Fs / 2); plt.ylim(0, Xm.max() * 1.3)
plt.xlabel("Frecuencia [Hz]"); plt.ylabel("|X_m(f)|")
plt.title("Espectro de magnitud de la señal combinada")
savefig("p1_combinada_espectro.png")

# ---------------------------------------------------------------- 1.D filtro pasa bajos FIR (Kaiser, fase lineal)
f_pass, f_stop, A_stop = 600.0, 1500.0, 60.0
numtaps, beta = signal.kaiserord(A_stop, (f_stop - f_pass) / (Fs / 2))
numtaps |= 1                                        # impar -> tipo I, retardo entero
f_cut = (f_pass + f_stop) / 2
h = signal.firwin(numtaps, f_cut, window=("kaiser", beta), fs=Fs)
D = (numtaps - 1) // 2                              # retardo de grupo [muestras]

wf, Hf = signal.freqz(h, worN=8192, fs=Fs)
fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
ax[0].plot(wf, 20 * np.log10(np.abs(Hf) + 1e-12))
ax[0].axvline(f_pass, ls="--", color="#555555"); ax[0].axvline(f_stop, ls="--", color="#555555")
ax[0].set_ylim(-110, 5); ax[0].set_ylabel("|H| [dB]")
ax[0].set_title(f"Filtro FIR Kaiser: {numtaps} coeficientes, β={beta:.2f}, banda de paso 0-{f_pass:.0f} Hz, rechazo desde {f_stop:.0f} Hz")
ax[1].plot(wf, np.unwrap(np.angle(Hf)))
ax[1].set_ylabel("Fase [rad]"); ax[1].set_xlabel("Frecuencia [Hz]")
ax[1].set_xlim(0, 4000)
savefig("p1_filtro_respuesta.png")

# ---------------------------------------------------------------- 1.F demodulación
def demodular(senal, k):
    y = 2 * np.cos(2 * np.pi * fc[k] / Fs * n) * senal
    y = np.r_[y, np.zeros(D)]                       # vaciar el filtro (cola)
    return signal.lfilter(h, 1.0, y)[D:]            # compensar el retardo D

xr = np.column_stack([demodular(xm, k) for k in range(5)])

fig, ax = plt.subplots(5, 1, figsize=(8, 9), sharex=True)
for k in range(5):
    ax[k].plot(t_ms, x[:, k], lw=1.6, label="original", color="#1f4e9c")
    ax[k].plot(t_ms, xr[:, k], lw=0.9, ls="--", label="recuperada", color="#e09f00")
    ax[k].set_ylabel(f"x{k+1}(n)")
    if k == 0: ax[k].legend(loc="upper right", ncol=2, fontsize=7)
ax[-1].set_xlabel("Tiempo [ms]")
fig.suptitle("Señales recuperadas sobre las originales (con compensación de retardo)")
savefig("p1_recuperadas.png")

# magnitud y fase
NF = 8192
fr2 = np.fft.rfftfreq(NF, 1 / Fs)
filas = []
fig, ax = plt.subplots(5, 2, figsize=(9, 10), sharex=True)
for k in range(5):
    X = np.fft.rfft(x[:, k], NF); Xr = np.fft.rfft(xr[:, k], NF)
    sig = np.abs(X) > 0.02 * np.abs(X).max()        # bins donde hay energía
    err_mag = np.max(np.abs(np.abs(Xr[sig]) - np.abs(X[sig])) / np.abs(X[sig]))
    err_ph = np.max(np.abs(np.angle(Xr[sig] * np.conj(X[sig]))))
    snr = 10 * np.log10(np.sum(x[:, k] ** 2) / np.sum((x[:, k] - xr[:, k]) ** 2))
    filas.append(dict(canal=k + 1, err_mag_rel_max=err_mag, err_fase_max_rad=err_ph,
                      err_fase_max_grados=np.degrees(err_ph), snr_db=snr))
    m = fr2 < 800
    ax[k, 0].plot(fr2[m], np.abs(X[m]), lw=1.6, color="#1f4e9c")
    ax[k, 0].plot(fr2[m], np.abs(Xr[m]), lw=0.9, ls="--", color="#e09f00")
    ax[k, 0].set_ylabel(f"|X{k+1}|")
    ph = np.where(sig, np.angle(X), np.nan); phr = np.where(sig, np.angle(Xr), np.nan)
    ax[k, 1].plot(fr2[m], ph[m], lw=1.6, color="#1f4e9c", label="original")
    ax[k, 1].plot(fr2[m], phr[m], lw=0.9, ls="--", color="#e09f00", label="recuperada")
    ax[k, 1].set_ylabel("fase [rad]")
    if k == 0: ax[k, 1].legend(fontsize=7)
ax[0, 0].set_title("Magnitud"); ax[0, 1].set_title("Fase (donde |X| > 2 % del máx.)")
ax[-1, 0].set_xlabel("Frecuencia [Hz]"); ax[-1, 1].set_xlabel("Frecuencia [Hz]")
savefig("p1_mag_fase.png")

lat = D / Fs
save_json("p1.json", dict(Fs=Fs, N=N, nyquist=Fs / 2, tabla=tabla, numtaps=numtaps, beta=beta,
                          f_pass=f_pass, f_stop=f_stop, f_cut=f_cut, A_stop=A_stop, D=D,
                          latencia_ms=lat * 1e3, filas=filas,
                          rizado_paso_db=float(np.max(np.abs(20 * np.log10(np.abs(Hf[wf <= 500]))))),
                          atenuacion_rechazo_db=float(-20 * np.log10(np.max(np.abs(Hf[wf >= f_stop]))))))
print(f"taps={numtaps} beta={beta:.3f} D={D} latencia={lat*1e3:.3f} ms")
for r in filas: print(r)
