#!/usr/bin/env python3
"""Pregunta 3 - Compresión de audio (ventaneo + DCT + cuantización + RLE).

Compresor:  ventanas de N=512 -> DCT -> cuantización Q(k) -> corte FC -> RLE -> bytes
Descompresor: bytes -> RLE inverso -> X_Q*Q -> iDCT -> concatenación / overlap-add
"""
import sys
import numpy as np
import scipy.fft as sfft
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
from common import savefig, save_json, DATA, ROOT
import os

N = 512
k_idx = np.arange(N)
Q = 1 + 10 ** (3 * k_idx / (2 * N))           # vector de cuantización Q(k)
HEADER_BYTES = 8                               # nº de muestras (uint32) + FC (float32)


# ------------------------------------------------------------------ ventaneo
def ventanas(x, overlap):
    """Divide x en ventanas de N muestras.
    overlap=True : Hann periódica con 50 % de traslape (suma 1 -> reconstrucción exacta
                   por overlap-add y sin discontinuidades de borde).
    overlap=False: ventanas contiguas sin traslape (rectangular)."""
    hop = N // 2 if overlap else N
    pad_f = hop if overlap else 0
    nfr = int(np.ceil((len(x) + pad_f) / hop)) + (1 if overlap else 0)
    xp = np.zeros(hop * (nfr + (0 if not overlap else 0)) + (N - hop))
    xp[pad_f:pad_f + len(x)] = x
    idx = np.arange(N)[None, :] + hop * np.arange(nfr)[:, None]
    fr = xp[idx]
    if overlap:
        fr = fr * np.hanning(N + 1)[:-1]       # Hann periódica
    return fr


# ------------------------------------------------------------------ RLE
def rle_ventana(q, cap=N):
    """RLE de ceros: cada racha de ceros -> (0, longitud). Los valores != 0 van tal cual."""
    out = []
    prev = -1
    for j in np.flatnonzero(q):
        z = j - prev - 1
        if z:
            out += (0, z)
        out.append(int(q[j]))
        prev = j
    z = len(q) - prev - 1
    if z:
        out += (0, z)
    return out


def rle_inverso(tokens, pos):
    """Decodifica UNA ventana (N coeficientes) a partir de tokens[pos]. Devuelve (ventana, nueva_pos)."""
    w = np.zeros(N, dtype=np.int64)
    m = 0
    while m < N:
        v = tokens[pos]
        if v == 0:
            m += tokens[pos + 1]               # racha de ceros ya está en 0
            pos += 2
        else:
            w[m] = v
            m += 1
            pos += 1
    return w, pos


# ------------------------------------------------------------------ empaquetado (rango dinámico)
def pack_varint(vals):
    """Enteros con signo -> bytes con zigzag + varint (LEB128): 1 byte si |v|<64, 2 si <8192, ..."""
    v = np.asarray(vals, dtype=np.int64)
    z = ((v << 1) ^ (v >> 63)).astype(np.uint64)
    nb = np.maximum(1, np.ceil(np.log2(z.astype(np.float64) + 1) / 7).astype(np.int64))
    starts = np.cumsum(nb) - nb
    out = np.zeros(int(nb.sum()), dtype=np.uint8)
    for b in range(int(nb.max())):
        sel = nb > b
        byte = ((z[sel] >> np.uint64(7 * b)) & np.uint64(0x7F)).astype(np.uint8)
        byte |= ((nb[sel] > b + 1).astype(np.uint8) << 7)
        out[starts[sel] + b] = byte
    return out


def unpack_varint(buf):
    buf = np.asarray(buf, dtype=np.uint8)
    last = ~(buf & 0x80).astype(bool)           # último byte de cada valor
    ends = np.flatnonzero(last)
    starts = np.r_[0, ends[:-1] + 1]
    pos_in = np.arange(len(buf)) - np.repeat(starts, ends - starts + 1)
    contrib = (buf & 0x7F).astype(np.uint64) << (7 * pos_in).astype(np.uint64)
    z = np.add.reduceat(contrib, starts)
    return ((z >> np.uint64(1)).astype(np.int64)) ^ (-(z & np.uint64(1)).astype(np.int64))


# ------------------------------------------------------------------ compresor / descompresor
def comprimir(x_int16, FC, overlap=True):
    x = x_int16.astype(np.float64)
    fr = ventanas(x, overlap)
    Xw = sfft.dct(fr, type=2, norm="ortho", axis=1)          # DCT por ventana
    XQ = np.rint(Xw / Q).astype(np.int64)                    # cuantización
    d = int(np.floor(N * FC))
    XQ[:, d:] = 0                                            # corte espectral
    tokens = []
    for w in XQ:
        tokens += rle_ventana(w)
    c = pack_varint(tokens)                                  # c(m) como bytes
    header = np.frombuffer(np.uint32(len(x)).tobytes() + np.float32(FC).tobytes(), dtype=np.uint8)
    return np.r_[header, c], XQ


def descomprimir(c, overlap=True):
    n = int(np.frombuffer(c[:4].tobytes(), dtype=np.uint32)[0])
    tokens = unpack_varint(c[HEADER_BYTES:]).tolist()
    hop = N // 2 if overlap else N
    pad_f = hop if overlap else 0
    nfr = int(np.ceil((n + pad_f) / hop)) + (1 if overlap else 0)
    pos = 0
    out = np.zeros(hop * nfr + (N - hop))
    for f in range(nfr):                                      # c(m) -> c_w(m)
        XQw, pos = rle_inverso(tokens, pos)                   # RLE inverso
        Xhat = XQw * Q                                        # recuperar rango
        xw = sfft.idct(Xhat, type=2, norm="ortho")            # iDCT
        out[f * hop:f * hop + N] += xw                        # concatenar / overlap-add
    return out[pad_f:pad_f + n]


def snr_db(x, xh):
    x = x.astype(np.float64)
    return 10 * np.log10(np.sum(x ** 2) / np.sum((x - xh) ** 2))


if __name__ == "__main__":
    fs, x = wavfile.read(os.path.join(DATA, "smash.wav"))
    bytes_x = x.nbytes                                        # int16 -> 2 B/muestra
    FCs = [0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80, 1.00]
    res = {}
    for ov in (True, False):
        CR, SNR = [], []
        for FC in FCs:
            c, _ = comprimir(x, FC, ov)
            xh = descomprimir(c, ov)
            CR.append(bytes_x / len(c)); SNR.append(snr_db(x, xh))
            print(f"overlap={ov!s:5} FC={FC:4.2f} fc={FC*fs/2/1e3:5.2f} kHz  bytes={len(c):8d} CR={CR[-1]:6.2f} SNR={SNR[-1]:6.2f} dB", flush=True)
        res[ov] = (CR, SNR)

    # energía espectral acumulada (justificación de la dispersidad)
    Xall = sfft.dct(ventanas(x.astype(float), False), norm="ortho", axis=1)
    e = np.sum(Xall ** 2, axis=0); ecum = np.cumsum(e) / e.sum()

    # ---- gráficos
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    for ov, lab, col in ((True, "Hann 50 % traslape", "#1f4e9c"), (False, "sin traslape", "#e09f00")):
        ax[0].plot(FCs, res[ov][0], "o-", label=lab, color=col, ms=4)
        ax[1].plot(FCs, res[ov][1], "o-", label=lab, color=col, ms=4)
    ax[0].set_xlabel("Factor de calidad FC"); ax[0].set_ylabel("CR"); ax[0].set_title("Razón de compresión"); ax[0].legend(fontsize=7)
    ax[1].set_xlabel("Factor de calidad FC"); ax[1].set_ylabel("SNR [dB]"); ax[1].set_title("Relación señal a ruido"); ax[1].legend(fontsize=7)
    savefig("p3_cr_snr_vs_fc.png")

    plt.figure(figsize=(5.5, 3.6))
    plt.plot(res[True][0], res[True][1], "o-", color="#1f4e9c", label="Hann 50 % traslape")
    plt.plot(res[False][0], res[False][1], "o-", color="#e09f00", label="sin traslape")
    for FC, cr, s in zip(FCs, *res[True]):
        plt.annotate(f"{FC:.2f}", (cr, s), fontsize=6, xytext=(3, 3), textcoords="offset points")
    plt.xlabel("CR"); plt.ylabel("SNR [dB]"); plt.title("Compromiso SNR vs CR (etiquetas = FC, con traslape)"); plt.legend(fontsize=7)
    savefig("p3_snr_vs_cr.png")

    plt.figure(figsize=(5.5, 3.2))
    plt.plot(np.arange(N) / N, 100 * ecum, color="#2a9d8f")
    plt.xlabel("k / N  (FC equivalente)"); plt.ylabel("Energía acumulada [%]")
    plt.title("Energía de la DCT concentrada en bajas frecuencias")
    savefig("p3_energia_acumulada.png")

    # audio reconstruido para escuchar
    os.makedirs(os.path.join(ROOT, "audio_reconstruido"), exist_ok=True)
    for FC in (0.15, 0.30, 0.50):
        c, _ = comprimir(x, FC, True)
        wavfile.write(os.path.join(ROOT, "audio_reconstruido", f"smash_FC{int(FC*100):02d}.wav"), fs,
                      np.clip(np.rint(descomprimir(c, True)), -32768, 32767).astype(np.int16))
    save_json("p3.json", dict(fs=fs, bytes_x=bytes_x, FCs=FCs, CR_overlap=res[True][0], SNR_overlap=res[True][1],
                              CR_nooverlap=res[False][0], SNR_nooverlap=res[False][1],
                              ecum={f"{q}": float(ecum[int(q * N) - 1]) for q in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5)}))
