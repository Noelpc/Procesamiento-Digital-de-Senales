"""Tarea 4 - H(z) = (1-a)/(1-a z^-k). Uso: python3 filtro.py [archivo.wav]"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import lfilter

def coefs(a, k):
    b = np.array([1 - a])
    den = np.zeros(k + 1); den[0] = 1; den[k] = -a
    return b, den

# 1. Diagrama de polos y ceros (a=0.8, k=10)
a, k = 0.8, 10
r = a ** (1 / k)
polos = r * np.exp(2j * np.pi * np.arange(k) / k)
fig, ax = plt.subplots(figsize=(5, 5))
ax.add_patch(plt.Circle((0, 0), 1, fill=False, ls="--", color="gray"))
ax.plot(polos.real, polos.imag, "x", ms=9, label=f"{k} polos, |p|={r:.4f}")
ax.plot([0], [0], "o", mfc="none", ms=9, label=f"{k} ceros en z=0")
ax.set_aspect("equal"); ax.grid(alpha=.3); ax.legend(loc="upper right", fontsize=8)
ax.set_xlabel("Re"); ax.set_ylabel("Im")
ax.set_title(r"Polos y ceros, $\alpha=0.8$, $k=10$")
fig.savefig("polos_ceros.png", dpi=150, bbox_inches="tight")

# 3. Filtrado de audio
wav = sys.argv[1] if len(sys.argv) > 1 else "test.wav"
Fs, x = wavfile.read(wav)
if x.ndim > 1: x = x[:, 0]
x = x.astype(np.float64) / 32768
for ms, al in [(50, .6), (250, .4), (500, .2)]:
    k = int(round(Fs * ms / 1000))
    b, den = coefs(al, k)
    y = lfilter(b, den, x)
    wavfile.write(f"salida_{ms}ms.wav", Fs, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    np.save(f"ref_{ms}ms.npy", y)
    fig, axs = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
    t = np.arange(len(x)) / Fs
    axs[0].plot(t, x, lw=.5); axs[0].set_title("Entrada")
    axs[1].plot(t, y, lw=.5); axs[1].set_title(f"Salida: k={k} ({ms} ms), alpha={al}")
    axs[1].set_xlabel("t [s]"); fig.tight_layout(); fig.savefig(f"senal_{ms}ms.png", dpi=120)
    print(f"{ms} ms: k={k}, alpha={al}, ok")
