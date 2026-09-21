import argparse
import numpy as np
import matplotlib.pyplot as plt

def alias(F, Fs):
    """Alias de F en [-Fs/2, Fs/2]."""
    return F - Fs*np.round(F/Fs)

p = argparse.ArgumentParser(description="Señal seno, su alias y muestras")
p.add_argument("F", type=float, help="frecuencia de la señal (Hz), cualquier real")
p.add_argument("Fs", type=float, help="frecuencia de muestreo (Hz)")
p.add_argument("ciclos", type=float, help="ciclos de la señal original a mostrar")
p.add_argument("--out", help="guardar figura en archivo")
a = p.parse_args()
F, Fs = a.F, a.Fs
Fa = alias(F, Fs)
T = a.ciclos/abs(F) if F != 0 else 10/Fs
u, un = (1, "s") if T >= 1 else (1e3, "ms") if T >= 1e-3 else (1e6, "µs")
t = np.linspace(0, T, int(max(2000, 40*max(abs(F), abs(Fa))*T)))
n = np.arange(0, int(np.floor(T*Fs + 1e-9)) + 1)
tn = n/Fs
s = lambda f, t: np.sin(2*np.pi*f*t)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(t*u, s(F, t), 'r', lw=.8, label=f"x(t), F={F:.4g} Hz")
if not np.isclose(Fa, F):
    ax.plot(t*u, s(Fa, t), 'k', lw=.8, label=f"x_alias(t), F={Fa:.4g} Hz")
ax.stem(tn*u, s(F, tn), linefmt='g-', markerfmt='go', basefmt=' ',
        label=f"x[n], Fs={Fs:g} Hz")
ax.axhline(0, color='gray', lw=.5)
ax.set(xlabel=f"t ({un})", ylabel="Amplitud", title="Tarea 1")
ax.legend(loc="upper right")
if a.out: fig.savefig(a.out, dpi=150, bbox_inches="tight")
else: plt.show()
