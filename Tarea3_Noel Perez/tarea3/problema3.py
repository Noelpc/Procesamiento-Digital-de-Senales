#!/usr/bin/env python3
"""Problema 3: Pirata de Efectos.

Un sistema LTI FIR en reposo queda definido por su respuesta al impulso h[n];
la salida ante cualquier entrada es y = x * h (convolucion).
  a) Identificar h_eco y h_rev alimentando un impulso unitario.
  b) Verificar y = x * h contra los efectos originales.
  c) FIR unico equivalente a la cascada: h_tot = h_eco * h_rev.
"""
import numpy as np
from scipy.signal import fftconvolve

from efectos_fir import eco, reverberacion

fs = 44100            # Hz; h depende de fs, usar la misma fs al clonar


def respuesta_impulso(efecto, fs, N=3 * fs):
    """h[n] = salida ante delta[n].

    La salida incluye la cola completa: len(salida) = N + L - 1, entonces
    L = len(salida) - N + 1. (No se recortan ceros: la salida trae ruido
    numerico ~1e-17 que impide un recorte exacto.)
    """
    d = np.zeros(N)
    d[0] = 1.0
    o = efecto(d, fs)
    return o[: len(o) - N + 1]


# ---------- a) Identificacion ----------
h_eco = respuesta_impulso(eco, fs)
h_rev = respuesta_impulso(reverberacion, fs)
print("=== Inciso a ===")
print(f"L_eco = {len(h_eco)} muestras ({len(h_eco) / fs:.2f} s)")
print(f"L_rev = {len(h_rev)} muestras ({len(h_rev) / fs:.2f} s)")
idx = np.nonzero(np.abs(h_eco) > 1e-9)[0]
print("impulsos del eco (t [s], peso):",
      [(round(float(i / fs), 3), round(float(h_eco[i]), 4)) for i in idx])

# ---------- b) Verificacion con entrada arbitraria ----------
x = np.random.default_rng(0).standard_normal(3 * fs)      # ruido blanco de 3 s
y_eco, y_rev = eco(x, fs), reverberacion(x, fs)
e_eco = np.max(np.abs(y_eco - fftconvolve(x, h_eco)))
e_rev = np.max(np.abs(y_rev - fftconvolve(x, h_rev)))
print("\n=== Inciso b ===")
print(f"eco : misma longitud = {len(y_eco) == len(x) + len(h_eco) - 1}, error max = {e_eco:.2e}")
print(f"rev : misma longitud = {len(y_rev) == len(x) + len(h_rev) - 1}, error max = {e_rev:.2e}")

# ---------- c) FIR unico equivalente a la cascada ----------
h_tot = fftconvolve(h_eco, h_rev)                          # L = L1 + L2 - 1
y_casc = reverberacion(eco(x, fs), fs)
y_tot = fftconvolve(x, h_tot)
e_tot = np.max(np.abs(y_casc - y_tot))
print("\n=== Inciso c ===")
print(f"L_tot = {len(h_tot)} (= {len(h_eco)} + {len(h_rev)} - 1)")
print(f"misma longitud = {len(y_casc) == len(y_tot)}, error max = {e_tot:.2e}, "
      f"allclose = {np.allclose(y_casc, y_tot, atol=1e-9)}")

np.save("h_tot.npy", h_tot)                                # FIR clonado para uso futuro
print("FIR clonado guardado en h_tot.npy (usar: y = np.convolve(x, h_tot))")
