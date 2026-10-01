#!/usr/bin/env python3
"""Tarea 2 - Punto 3: eco mediante convolución.

Respuesta al impulso:  h(n) = δ(n) + A·δ(n - D),   D = round(retraso · fs)
Salida:  y(n) = x(n) * h(n) = x(n) + A·x(n - D)

Uso: python3 eco.py archivo.wav AMPLITUD RETRASO_S      ->  archivo_out.wav
Acepta cualquier formato de muestra PCM/float y cualquier número de canales;
la salida conserva ambos. Dependencias: numpy, soundfile.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def respuesta_eco(A, D):
    """h(n) = δ(n) + A δ(n-D), de longitud D+1."""
    h = np.zeros(D + 1)
    h[0] = 1.0
    h[D] += A          # si D == 0, h(0) = 1 + A
    return h


def convolucion_eco(x, h):
    """Convolución de x (N, canales) con h dispersa (impulsos en 0 y D).

    Como x*δ(n-k) = x(n-k), basta sumar copias desplazadas de x ponderadas
    por los impulsos de h. Equivale a np.convolve(x, h) pero en O(N)
    en lugar de O(N·D).
    """
    N, canales = x.shape
    y = np.zeros((N + h.size - 1, canales))
    for k in np.flatnonzero(h):
        y[k:k + N] += h[k] * x
    return y


def main():
    p = argparse.ArgumentParser(description="Agrega un eco a un archivo WAV.")
    p.add_argument("entrada", help="archivo WAV de entrada")
    p.add_argument("amplitud", type=float, help="amplitud relativa del eco, 0..1")
    p.add_argument("retraso", type=float, help="retraso del eco en segundos (>= 0)")
    a = p.parse_args()

    if not 0.0 <= a.amplitud <= 1.0:
        sys.exit("Error: la amplitud debe estar entre 0 y 1 (inclusive).")
    if a.retraso < 0:
        sys.exit("Error: el retraso debe ser >= 0.")

    info = sf.info(a.entrada)                      # fs, canales, subtipo (bits)
    x, fs = sf.read(a.entrada, dtype="float64", always_2d=True)  # [-1, 1]

    D = int(round(a.retraso * fs))                 # retraso en muestras
    h = respuesta_eco(a.amplitud, D)
    y = convolucion_eco(x, h)

    # Longitud teórica N + M - 1 = N + D
    assert y.shape[0] == x.shape[0] + h.size - 1

    pico = np.max(np.abs(y))
    if pico > 1.0 and not info.subtype.startswith("FLOAT") and info.subtype != "DOUBLE":
        y /= pico                                  # evita saturar formatos enteros
        print(f"Aviso: pico {pico:.3f} > 1; salida escalada por 1/{pico:.3f}")

    ruta = Path(a.entrada)
    salida = ruta.with_name(ruta.stem + "_out" + ruta.suffix)
    sf.write(salida, y, fs, subtype=info.subtype, format="WAV")
    print(f"{salida}: fs={fs} Hz, canales={info.channels}, formato={info.subtype}, "
          f"D={D} muestras ({D/fs:.4f} s), duración {y.shape[0]/fs:.3f} s")


if __name__ == "__main__":
    main()
