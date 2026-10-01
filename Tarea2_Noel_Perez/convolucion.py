#!/usr/bin/env python3
"""Tarea 2 - Punto 2: convolución de una señal de audio con una respuesta al impulso.

Uso: python3 convolucion.py [señal.wav] [respuesta_al_impulso.npy] [salida.wav]
Dependencias: numpy, scipy (ver requirements.txt). Requiere wav_io.py.
"""
import sys
import numpy as np
from wav_io import leer_wav, a_flotante, escribir_wav


def main():
    ruta_wav = sys.argv[1] if len(sys.argv) > 1 else "señal.wav"
    ruta_h = sys.argv[2] if len(sys.argv) > 2 else "respuesta_al_impulso.npy"
    ruta_out = sys.argv[3] if len(sys.argv) > 3 else "señal_convolucionada.wav"

    # a) Cargar señal y respuesta al impulso
    fs, datos = leer_wav(ruta_wav)
    x = a_flotante(datos)
    h = np.load(ruta_h).astype(np.float64).ravel()
    x = x[:, None] if x.ndim == 1 else x          # (N, canales)
    N, canales = x.shape
    M = h.size
    print(f"x: N={N} muestras, {canales} canal(es), fs={fs} Hz")
    print(f"h: M={M} muestras")

    # b) Convolución y(n) = sum_k x(k) h(n-k), canal por canal (numpy.convolve)
    y = np.stack([np.convolve(x[:, c], h) for c in range(canales)], axis=1)

    # c) Longitud teórica: N + M - 1
    teorica = N + M - 1
    print(f"Longitud teórica N+M-1 = {teorica}; obtenida = {y.shape[0]}; "
          f"coincide: {teorica == y.shape[0]}")

    # d) Normalizar solo si excede [-1, 1] (evita saturación) y escribir WAV
    pico = np.max(np.abs(y))
    if pico > 1.0:
        y = y / pico
        print(f"Pico {pico:.3f} > 1: se normalizó por {pico:.3f} para evitar saturación")
    y = y[:, 0] if canales == 1 else y
    escribir_wav(ruta_out, fs, y, np.int16)
    print(f"Escrito: {ruta_out} ({y.shape[0]/fs:.3f} s)")


if __name__ == "__main__":
    main()
